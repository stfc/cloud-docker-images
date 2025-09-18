package controllers

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gophercloud/gophercloud/v2"
	"github.com/gophercloud/gophercloud/v2/openstack/compute/v2/servers"
	"github.com/gophercloud/gophercloud/v2/openstack/identity/v3/users"
	"github.com/stretchr/testify/assert"
)

type mockServerResult struct {
	mockUserID string
	mockError  error
}

func (m mockServerResult) Extract() (*servers.Server, error) {
	return &servers.Server{
		Name: m.mockUserID,
	}, m.mockError
}

type mockUserResult struct {
	mockUserName string
	mockError    error
}

func (m mockUserResult) Extract() (*users.User, error) {
	return &users.User{
		Name: m.mockUserName,
	}, m.mockError
}

func TestServe_Success(t *testing.T) {
	// Patch both
	origServers := getServers
	origUsers := getUsers
	defer func() {
		getServers = origServers
		getUsers = origUsers
	}()

	getServers = func(ctx context.Context, client *gophercloud.ServiceClient, id string) ServerResult {
		return mockServerResult{
			mockUserID: "test-user-id",
			mockError:  nil,
		}
	}
	getUsers = func(ctx context.Context, client *gophercloud.ServiceClient, id string) UserResult {
		return mockUserResult{
			mockUserName: "mock-username",
			mockError:    nil,
		}
	}

	controller := &UsernameServiceController{}
	req := httptest.NewRequest("GET", "/username?serverID=test-server-id", nil)
	w := httptest.NewRecorder()

	controller.Serve(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.Equal(t, "mock-username", w.Body.String())
}

func TestGServe_MissingServerID(t *testing.T) {
	controller := &UsernameServiceController{}

	req := httptest.NewRequest("GET", "/username", nil)
	w := httptest.NewRecorder()

	controller.Serve(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
	assert.Contains(t, w.Body.String(), "missing serverID")
}

func TestServe_ServerLookupFails(t *testing.T) {
	original := getServers
	defer func() { getServers = original }()

	getServers = func(ctx context.Context, client *gophercloud.ServiceClient, id string) ServerResult {
		return mockServerResult{
			mockUserID: "",
			mockError:  fmt.Errorf("server not found"),
		}
	}

	controller := &UsernameServiceController{}

	req := httptest.NewRequest("GET", "/username?serverID=test-server", nil)
	w := httptest.NewRecorder()

	controller.Serve(w, req)

	assert.Equal(t, http.StatusInternalServerError, w.Code)
	assert.Contains(t, w.Body.String(), "error fetching server user ID")
}

func TestServe_UserLookupFails(t *testing.T) {
	originalServers := getServers
	originalUsers := getUsers
	defer func() {
		getServers = originalServers
		getUsers = originalUsers
	}()

	getServers = func(ctx context.Context, client *gophercloud.ServiceClient, id string) ServerResult {
		return mockServerResult{
			mockUserID: "test-user-id",
			mockError:  nil,
		}
	}

	getUsers = func(ctx context.Context, client *gophercloud.ServiceClient, id string) UserResult {
		return mockUserResult{
			mockUserName: "",
			mockError:    fmt.Errorf("user not found"),
		}
	}

	controller := &UsernameServiceController{}

	req := httptest.NewRequest("GET", "/username?serverID=test-server", nil)
	w := httptest.NewRecorder()

	controller.Serve(w, req)

	assert.Equal(t, http.StatusInternalServerError, w.Code)
	assert.Contains(t, w.Body.String(), "error fetching username")
}
