package main

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"
	"os"

	"github.com/gophercloud/gophercloud/v2"
	"github.com/gophercloud/gophercloud/v2/openstack"
	"github.com/gophercloud/gophercloud/v2/openstack/compute/v2/servers"
	"github.com/gophercloud/gophercloud/v2/openstack/config"
	"github.com/gophercloud/gophercloud/v2/openstack/config/clouds"
	"github.com/gophercloud/gophercloud/v2/openstack/identity/v3/users"
)

var identityClient *gophercloud.ServiceClient
var computeClient *gophercloud.ServiceClient

func init() {
	ctx := context.Background()

	var err error
	authOptions, endpointOptions, tlsConfig, err := clouds.Parse(clouds.WithCloudName("openstack"))
	if err != nil {
		panic(err)
	}

	authOptions.AllowReauth = true

	providerClient, err := config.NewProviderClient(ctx, authOptions, config.WithTLSConfig(tlsConfig))
	if err != nil {
		panic(err)
	}

	computeClient, err = openstack.NewComputeV2(providerClient, endpointOptions)
	if err != nil {
		slog.Error("Failed to initilize compute client")
		panic(err)
	}
	identityClient, err = openstack.NewIdentityV3(providerClient, endpointOptions)
	if err != nil {
		slog.Error("Failed to initilize compute client")
		panic(err)
	}
}

func getServerUserID(computeClient *gophercloud.ServiceClient, serverID string) (string, error) {
	// Get the user ID associated with a given server
	server := servers.Get(context.TODO(), computeClient, serverID)
	serverDetails, err := server.Extract()
	if err != nil {
		slog.Error("Failed to get server details", "ID", serverID)
		return "", err
	}

	return serverDetails.UserID, nil
}

func getUsername(identityClient *gophercloud.ServiceClient, userID string) (string, error) {
	// Get the username associated with a given user ID
	user := users.Get(context.TODO(), identityClient, userID)
	userDetails, err := user.Extract()
	if err != nil {
		slog.Error("Failed to get user details", "ID", userID)
		return "", err
	}
	return userDetails.Name, nil

}

func main() {

	addr := os.Getenv("ADDR")
	if addr == "" {
		addr = ":80"
	}

	http.HandleFunc("/getusername", getUserHandler)
	err := http.ListenAndServe(addr, nil)
	if err != nil {
		slog.Error("Failed to start server", "addr", addr)
		panic(err)
	}
}

func getUserHandler(w http.ResponseWriter, r *http.Request) {

	serverID := r.URL.Query().Get("serverID")
	userID, err := getServerUserID(computeClient, serverID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	name, err := getUsername(identityClient, userID)
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
