package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"

	"github.com/gophercloud/gophercloud/v2"
	"github.com/gophercloud/gophercloud/v2/openstack/compute/v2/servers"
	"github.com/gophercloud/gophercloud/v2/openstack/identity/v3/users"
)

type service struct {
	client OpenstackClient
}

// Get the user ID associated with a given server
func getServerUserID(computeClient *gophercloud.ServiceClient, serverID string) (string, error) {
	server := servers.Get(context.TODO(), computeClient, serverID)
	serverDetails, err := server.Extract()
	if err != nil {
		slog.Error("Failed to get server details", "ID", serverID)
		return "", err
	}

	return serverDetails.UserID, nil
}

// Get the username associated with a given user ID
func getUsername(identityClient *gophercloud.ServiceClient, userID string) (string, error) {
	user := users.Get(context.TODO(), identityClient, userID)
	userDetails, err := user.Extract()
	if err != nil {
		slog.Error("Failed to get user details", "ID", userID)
		return "", err
	}

	return userDetails.Name, nil
}

// Handle requests to the path: .../getusername?serverID=<ID>
func (s service) getUserHandler(w http.ResponseWriter, r *http.Request) {

	serverID := r.URL.Query().Get("serverID")
	userID, err := getServerUserID(s.client.identityClient, serverID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	name, err := getUsername(s.client.identityClient, userID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	_, err = fmt.Fprintf(w, "%s", name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func main() {

	addr := os.Getenv("ADDR")
	if addr == "" {
		addr = ":80"
	}

	var client OpenstackClient
	client.New("openstack")

	service := service{client: client}

	http.HandleFunc("/getusername", service.getUserHandler)
	err := http.ListenAndServe(addr, nil)
	if err != nil {
		slog.Error("Failed to start server", "addr", addr)
		panic(err)
	}
}
