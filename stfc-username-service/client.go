package main

import (
	"context"
	"log/slog"

	"github.com/gophercloud/gophercloud/v2"
	"github.com/gophercloud/gophercloud/v2/openstack"
	"github.com/gophercloud/gophercloud/v2/openstack/config"
	"github.com/gophercloud/gophercloud/v2/openstack/config/clouds"
)

type OpenstackClient struct {
	computeClient  *gophercloud.ServiceClient
	identityClient *gophercloud.ServiceClient
}

func (c *OpenstackClient) New(cloud string) {
	ctx := context.Background()

	authOptions, endpointOptions, tlsConfig, err := clouds.Parse(clouds.WithCloudName(cloud))
	if err != nil {
		panic(err)
	}

	authOptions.AllowReauth = true

	providerClient, err := config.NewProviderClient(ctx, authOptions, config.WithTLSConfig(tlsConfig))
	if err != nil {
		panic(err)
	}

	c.computeClient, err = openstack.NewComputeV2(providerClient, endpointOptions)
	if err != nil {
		slog.Error("Failed to initilize compute client")
		panic(err)
	}
	c.identityClient, err = openstack.NewIdentityV3(providerClient, endpointOptions)
	if err != nil {
		slog.Error("Failed to initilize identity client")
		panic(err)
	}

}
