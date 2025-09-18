package controllers

import (
	"context"
	"fmt"
	"log/slog"
	"net/http"

	"github.com/gophercloud/gophercloud/v2"
	"github.com/gophercloud/gophercloud/v2/openstack/compute/v2/servers"
	"github.com/gophercloud/gophercloud/v2/openstack/identity/v3/users"
)

type ServerResult interface {
	Extract() (*servers.Server, error)
}

type UserResult interface {
	Extract() (*users.User, error)
}

type ServerGetter func(ctx context.Context, client *gophercloud.ServiceClient, id string) ServerResult
type UserGetter func(ctx context.Context, client *gophercloud.ServiceClient, id string) UserResult

// wrap in function variables to allow mocking in tests
var (
	getServers ServerGetter = func(ctx context.Context, client *gophercloud.ServiceClient, id string) ServerResult {
		return servers.Get(ctx, client, id)
	}
	getUsers UserGetter = func(ctx context.Context, client *gophercloud.ServiceClient, id string) UserResult {
		return users.Get(ctx, client, id)
	}
)

type UsernameServiceController struct {
	ComputeClient  *gophercloud.ServiceClient
	IdentityClient *gophercloud.ServiceClient
}

func (uc *UsernameServiceController) getUserID(ctx context.Context, serverID string) (string, error) {
	result := getServers(ctx, uc.ComputeClient, serverID)
	serverDetails, err := result.Extract()
	if err != nil {
		return "", err
	}
	return serverDetails.UserID, nil
}

func (uc *UsernameServiceController) getUserName(ctx context.Context, userID string) (string, error) {
	result := getUsers(ctx, uc.IdentityClient, userID)
	userDetails, err := result.Extract()
	if err != nil {
		return "", err
	}
	return userDetails.Name, nil
}

func (uc *UsernameServiceController) Serve(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	serverID := r.URL.Query().Get("serverID")
	if serverID == "" {
		http.Error(w, "missing serverID", http.StatusBadRequest)
		return
	}

	userID, err := uc.getUserID(ctx, serverID)
	if err != nil {
		slog.Error("Failed to get userID associated with serverID",
			serverID,
			slog.String("error", err.Error()),
		)
		http.Error(w, fmt.Sprintf("error fetching server user ID: %v", err), http.StatusInternalServerError)
		return
	}

	userName, err := uc.getUserName(ctx, userID)
	if err != nil {
		slog.Error(
			"Failed to get user name associated with userID",
			userID,
			slog.String("error", err.Error()),
		)
		http.Error(w, fmt.Sprintf("error fetching username: %v", err), http.StatusInternalServerError)
		return
	}

	_, err = fmt.Fprintf(w, "%s", userName)
	if err != nil {
		slog.Error("Failed to write response", slog.String("error", err.Error()))
		http.Error(w, fmt.Sprintf("failed writing response: %v", err), http.StatusInternalServerError)
		return
	}
}
