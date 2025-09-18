package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"

	"cloudsetup/controllers"
	"cloudsetup/routes"

	"github.com/gophercloud/gophercloud/v2"
	"github.com/gophercloud/gophercloud/v2/openstack"
	"github.com/gophercloud/gophercloud/v2/openstack/config"
	"github.com/gophercloud/gophercloud/v2/openstack/config/clouds"
)

type ExternalClients struct {
	ComputeClient  *gophercloud.ServiceClient
	IdentityClient *gophercloud.ServiceClient
}

// Package-level variables for mocking external dependencies
var (
	cloudsParse             = clouds.Parse
	configNewProviderClient = config.NewProviderClient
	openstackNewComputeV2   = openstack.NewComputeV2
	openstackNewIdentityV3  = openstack.NewIdentityV3
	httpListenAndServe      = http.ListenAndServe
	osGetenv                = os.Getenv
	slogInfo                = slog.Info
	slogError               = slog.Error
)

func setupExternalClients(ctx context.Context, cloudAccount string) (*ExternalClients, error) {
	authOpts, endpointOpts, tlsConfig, err := cloudsParse(clouds.WithCloudName(cloudAccount))
	if err != nil {
		return nil, err
	}
	authOpts.AllowReauth = true

	provider, err := configNewProviderClient(ctx, authOpts, config.WithTLSConfig(tlsConfig))
	if err != nil {
		return nil, err
	}

	computeClient, err := openstackNewComputeV2(provider, endpointOpts)
	if err != nil {
		return nil, err
	}

	identityClient, err := openstackNewIdentityV3(provider, endpointOpts)
	if err != nil {
		return nil, err
	}

	return &ExternalClients{
		ComputeClient:  computeClient,
		IdentityClient: identityClient,
	}, nil
}

func setupControllers(clients *ExternalClients) *routes.AllControllers {
	// setup controllers here
	usercontroller := &controllers.UsernameServiceController{
		ComputeClient:  clients.ComputeClient,
		IdentityClient: clients.IdentityClient,
	}
	ctrls := &routes.AllControllers{
		UsernameServiceController: usercontroller,
	}
	return ctrls
}

func setupRoutes(ctrls *routes.AllControllers) *http.ServeMux {
	mux := http.NewServeMux()
	routes.RegisterRoutes(mux, ctrls)
	return mux
}

func serve(addr string, handler http.Handler) error {
	slogInfo("Starting server", "addr", addr)
	return httpListenAndServe(addr, handler)
}

func main() {
	ctx := context.Background()
	clients, err := setupExternalClients(ctx, "openstack")
	if err != nil {
		slogError("Failed to setup clients", "error", err)
		panic(err)
	}

	ctrls := setupControllers(clients)
	mux := setupRoutes(ctrls)

	addr := osGetenv("ADDR")
	if addr == "" {
		addr = ":80"
	}

	if err := serve(addr, mux); err != nil {
		slogError("Server failed", "error", err)
		panic(err)
	}
}
