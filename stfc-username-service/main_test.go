package main

import (
	"fmt"
	"net/http"
	"testing"

	"github.com/gophercloud/gophercloud/v2/testhelper"
	"github.com/gophercloud/gophercloud/v2/testhelper/client"
)

type response func()

func TestUserNameFailure(t *testing.T) {
	tests := []struct {
		desc      string
		arg       string
		fake      response
		expOutput string
		expErr    string
	}{{
		desc: "user find error",
		arg:  "abc123",
	}}

	for _, tt := range tests {
		t.Run(tt.desc, func(t *testing.T) {
			fakeserver := testhelper.SetupHTTP()
			defer fakeserver.Teardown()
			url := "/users/" + tt.arg
			fakeserver.Mux.HandleFunc(url, func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusNotFound)
			})
			c := client.ServiceClient(fakeserver)

			r, err := getUsername(c, tt.arg)
			testhelper.AssertErr(t, err)
			testhelper.AssertEquals(t, r, "")
		})
	}
}

func TestUserNameSuccess(t *testing.T) {
	tests := []struct {
		desc      string
		arg       string
		fake      response
		expOutput string
		expErr    string
	}{{
		desc:      "user find success",
		arg:       "abc123",
		expOutput: "test_user",
	}}

	for _, tt := range tests {
		t.Run(tt.desc, func(t *testing.T) {
			fakeserver := testhelper.SetupHTTP()
			defer fakeserver.Teardown()
			url := "/users/" + tt.arg
			fakeserver.Mux.HandleFunc(url, func(w http.ResponseWriter, r *http.Request) {
				w.Header().Add("Content-Type", "application/json")
				_, err := fmt.Fprintf(w, `
							{
								"user": 
									{
										"id": "abc123",
										"name": "test_user"
									}
							}
						`)
				if err != nil {
					http.Error(w, err.Error(), http.StatusInternalServerError)
					return
				}
			})
			c := client.ServiceClient(fakeserver)

			r, err := getUsername(c, tt.arg)
			testhelper.AssertNoErr(t, err)
			testhelper.AssertEquals(t, r, "test_user")
		})
	}
}

func TestServerUserIDFailure(t *testing.T) {
	tests := []struct {
		desc      string
		arg       string
		fake      response
		expOutput string
		expErr    string
	}{{
		desc: "server user ID find error",
		arg:  "xyz321",
	}}

	for _, tt := range tests {
		t.Run(tt.desc, func(t *testing.T) {
			fakeserver := testhelper.SetupHTTP()
			defer fakeserver.Teardown()
			url := "/servers/" + tt.arg
			fakeserver.Mux.HandleFunc(url, func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusNotFound)
			})
			c := client.ServiceClient(fakeserver)

			r, err := getServerUserID(c, tt.arg)
			testhelper.AssertErr(t, err)
			testhelper.AssertEquals(t, r, "")
		})
	}
}

func TestServerUserIDSuccess(t *testing.T) {
	tests := []struct {
		desc      string
		arg       string
		fake      response
		expOutput string
		expErr    string
	}{{
		desc:      "server user ID find success",
		arg:       "xyz321",
		expOutput: "abc123",
	}}

	for _, tt := range tests {
		t.Run(tt.desc, func(t *testing.T) {
			fakeserver := testhelper.SetupHTTP()
			defer fakeserver.Teardown()
			url := "/servers/" + tt.arg
			fakeserver.Mux.HandleFunc(url, func(w http.ResponseWriter, r *http.Request) {
				w.Header().Add("Content-Type", "application/json")
				_, err := fmt.Fprintf(w, `
							{
								"server": 
									{
										"id": "xyz321",
										"user_id": "abc123"
									}
							}
						`)
				if err != nil {
					http.Error(w, err.Error(), http.StatusInternalServerError)
					return
				}
			})
			c := client.ServiceClient(fakeserver)

			r, err := getServerUserID(c, tt.arg)
			testhelper.AssertNoErr(t, err)
			testhelper.AssertEquals(t, r, "abc123")
		})
	}
}
