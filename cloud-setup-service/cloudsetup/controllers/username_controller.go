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

type UsernameServiceController struct {
	ComputeClient  *gophercloud.ServiceClient
	IdentityClient *gophercloud.ServiceClient
}

func (uc *UsernameServiceController) GetUserID(ctx context.Context, serverID string) (string, error) {
	result := servers.Get(ctx, uc.ComputeClient, serverID)
	serverDetails, err := result.Extract()
	if err != nil {
		return "", err
	}
	return serverDetails.UserID, nil
}

func (uc *UsernameServiceController) GetUserName(ctx context.Context, userID string) (string, error) {
	result := users.Get(ctx, uc.IdentityClient, userID)
	userDetails, err := result.Extract()
	if err != nil {
		return "", err
	}
	return userDetails.Name, nil
}

func (uc *UsernameServiceController) GetUsernameHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	serverID := r.URL.Query().Get("serverID")
	if serverID == "" {
		http.Error(w, "missing serverID", http.StatusBadRequest)
		return
	}

	userID, err := uc.GetUserID(ctx, serverID)
	if err != nil {
		slog.Error("Failed to get userID associated with serverID", serverID, "error", err)
		http.Error(w, fmt.Sprintf("error fetching server user ID: %v", err), http.StatusInternalServerError)
		return
	}

	userName, err := uc.GetUserName(ctx, userID)
	if err != nil {
		slog.Error("Failed to get user name associated with userID", userID, "error", err)
		http.Error(w, fmt.Sprintf("error fetching username: %v", err), http.StatusInternalServerError)
		return
	}

	_, err = fmt.Fprintf(w, "%s", userName)
	if err != nil {
		slog.Error("Failed to write response", "error", err)
		http.Error(w, fmt.Sprintf("failed writing response: %v", err), http.StatusInternalServerError)
		return
	}
}
