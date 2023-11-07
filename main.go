package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

const userAgent = "github.com/Jorropo/peerTube-autoDiscover"

var logger = log.Default()

var nodes = map[string]struct{}{}
var nodesLk sync.Mutex
var goodNodes = map[string]struct{}{}
var goodNodesLk sync.Mutex
var wg sync.WaitGroup

// foundNode must be called while holding [nodesLk].
func foundNode(from, node string) {
	if _, ok := nodes[node]; ok {
		return
	}
	nodes[node] = struct{}{}

	logger.Printf("found %s from %s\n", node, from)

	wg.Add(2)
	go queryNode(node, false)
	go queryNode(node, true)
}

type Add struct {
	Host string `json:"host"`
}

func addToInstancesList(node string) {
	defer wg.Done()

	if err := func() error {
		format, err := json.Marshal(Add{node})
		if err != nil {
			return fmt.Errorf("serializing: %w", err)
		}

		req, err := http.NewRequest(http.MethodPost, "https://instances.joinpeertube.org/api/v1/instances", bytes.NewReader(format))
		if err != nil {
			return fmt.Errorf("creating the request: %w", err)
		}
		req.Header.Add("User-Agent", userAgent)
		req.Header.Add("Content-Type", "application/json")

		res, err := http.DefaultClient.Do(req)
		if err != nil {
			return fmt.Errorf("POSTing: %w", err)
		}
		res.Body.Close()

		if res.StatusCode != http.StatusOK {
			return fmt.Errorf("got http %d instead of 200", res.StatusCode)
		}

		return nil
	}(); err != nil {
		logger.Printf("error adding %s: %s", node, err)
	}
}

func foundGoodNode(node string) {
	if goodNodesLk.TryLock() {
		// optimistic path hopping querying instances.joinpeertube.org finished.
		defer goodNodesLk.Unlock()

		if _, ok := goodNodes[node]; ok {
			return
		}
		goodNodes[node] = struct{}{}

		wg.Add(1)
		go addToInstancesList(node)
		return
	}

	// slow path while we are still waiting
	wg.Add(1)
	go func() {
		goodNodesLk.Lock()
		if _, ok := goodNodes[node]; ok {
			goodNodesLk.Unlock()
			wg.Done()
			return
		}
		goodNodes[node] = struct{}{}
		goodNodesLk.Unlock()

		// addToInstancesList will call wg.Done
		addToInstancesList(node)
	}()
}

type nodeResponse struct {
	Total uint `json:"total"`
	Data  []struct {
		Follower struct {
			Host string `json:"host"`
		} `json:"follower"`
		Following struct {
			Host string `json:"host"`
		} `json:"following"`
	} `json:"data"`
}

func doRequestToNode(node string, queryFollower bool, skip uint) (out nodeResponse, err error) {
	verb := "following"
	if queryFollower {
		verb = "followers"
	}

	firstUrl := "https://" + node + "/api/v1/server/" + verb + "?count=100"

	if skip != 0 {
		firstUrl += "&start=" + strconv.FormatUint(uint64(skip), 10)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, firstUrl, nil)
	if err != nil {
		return out, fmt.Errorf("creating the request: %w", err)
	}
	req.Header.Add("User-Agent", userAgent)

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return out, fmt.Errorf("requesting: %w", err)
	}
	defer res.Body.Close()

	if res.StatusCode != http.StatusOK {
		return out, fmt.Errorf("got http %d instead of 200", res.StatusCode)
	}

	if err := json.NewDecoder(res.Body).Decode(&out); err != nil {
		return out, fmt.Errorf("parsing json: %w", err)
	}

	nodesLk.Lock()
	defer nodesLk.Unlock()
	foundGoodNode(node)
	for _, v := range out.Data {
		var new string
		if queryFollower {
			new = v.Follower.Host
		} else {
			new = v.Following.Host
		}
		foundNode(node, new)
	}

	return
}

func queryNode(node string, queryFollower bool) {
	defer wg.Done()

	if err := func() error {
		info, err := doRequestToNode(node, queryFollower, 0)
		if err != nil {
			return fmt.Errorf("initial query: %w", err)
		}

		if info.Total == 100 || len(info.Data) != 100 {
			// we got the complete data already
			return nil
		}

		remaining := info.Total - 100
		iterationRequests := remaining / 100
		if remaining%100 != 0 {
			// round up
			iterationRequests++
		}

		wg.Add(int(iterationRequests * 2))
		// we query off by one since we already queried the first 100 when querying the total
		for i := iterationRequests; i != 0; i-- {
			schedule := func(i uint, queryFollower bool) {
				defer wg.Done()

				if _, err := doRequestToNode(node, queryFollower, i*100); err != nil {
					logger.Printf("error with %s: secondary query: %s\n", node, err)
				}
			}
			go schedule(i, false)
			go schedule(i, true)
		}
		return nil
	}(); err != nil {
		logger.Printf("error with %s: %s\n", node, err)
	}
}

type instancesListResponse struct {
	Total uint `json:"total"`
	Data  []struct {
		Host string `json:"host"`
	} `json:"data"`
}

func doRequestToInstanceList(skip uint) (out instancesListResponse, err error) {
	firstUrl := "https://instances.joinpeertube.org/api/v1/instances?count=100"

	if skip != 0 {
		firstUrl += "&start=" + strconv.FormatUint(uint64(skip), 10)
	}

	req, err := http.NewRequest(http.MethodGet, firstUrl, nil)
	if err != nil {
		return out, fmt.Errorf("creating the request: %w", err)
	}
	req.Header.Add("User-Agent", userAgent)

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return out, fmt.Errorf("requesting: %w", err)
	}
	defer res.Body.Close()

	if res.StatusCode != http.StatusOK {
		return out, fmt.Errorf("got http %d instead of 200", res.StatusCode)
	}

	if err := json.NewDecoder(res.Body).Decode(&out); err != nil {
		return out, fmt.Errorf("parsing json: %w", err)
	}

	nodesLk.Lock()
	defer nodesLk.Unlock()
	for _, v := range out.Data {
		foundNode("instances.joinpeertube.org", v.Host)
	}

	return
}

func main() {
	// keep that locked while we download from the instance list
	goodNodesLk.Lock()

	// scan
	if len(os.Args) > 1 {
		nodesLk.Lock()
		for _, v := range os.Args[1:] {
			foundNode("os.Args", v)
		}
		nodesLk.Unlock()
	}

	// we can't rely on goodNodesLk since nodes are waiting on it to know when quering the instance list was finished
	var localGoodNodesLk sync.Mutex
	var goodNodesWg sync.WaitGroup

	// download from the instance list
	if err := func() error {
		info, err := doRequestToInstanceList(0)
		if err != nil {
			return fmt.Errorf("initial query: %w", err)
		}

		for _, v := range info.Data {
			goodNodes[v.Host] = struct{}{}
		}

		remaining := info.Total - 100
		iterationRequests := remaining / 100
		if remaining%100 != 0 {
			// round up
			iterationRequests++
		}

		goodNodesWg.Add(int(iterationRequests))
		// we query off by one since we already queried the first 100 when querying the total
		for i := iterationRequests; i != 0; i-- {
			go func(i uint) {
				defer goodNodesWg.Done()

				info, err := doRequestToInstanceList(i * 100)
				if err != nil {
					logger.Fatalf("secondary query to the instance list: %s\n", err)
				}

				localGoodNodesLk.Lock()
				for _, v := range info.Data {
					goodNodes[v.Host] = struct{}{}
				}
				localGoodNodesLk.Unlock()
			}(i)
		}

		return nil
	}(); err != nil {
		logger.Fatalf("querying instance list: %s\n", err)
	}

	goodNodesWg.Wait()
	countBefore := len(goodNodes)
	goodNodesLk.Unlock()

	wg.Wait()
	logger.Printf("found %d nodes, %d good nodes and %d new good nodes\n", len(nodes), len(goodNodes), len(goodNodes)-countBefore)
}
