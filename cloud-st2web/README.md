# Stackstorm Web container - st2web for SSO   

This container is built from upstream - github.com/StackStorm/st2-dockerfiles/tree/master/st2web
with a few tweaks to have an oauth2-proxy frontend service handling TLS and authentication via IRIS IAM 

In order to use IRIS IAM - we setup st2auth to be in proxy mode - https://docs.stackstorm.com/authentication.html#proxy-auth-mode

st2web does not seem to have native support for st2auth proxy mode. 

There's 3 fundamental problems: 

- st2auth only accepts “CGI” parameters. While the documentation explains that “CGI” parameters are used by st2auth, it does not explain how these should be passed. 

- The front-end only supports standalone mode (it does not retrieve a token for you, when in proxy mode).

- Internal tools (the st2 command line utility) only support standalone mode (they’ll only do a basic auth request to auth backend, which is not accepted in proxy mode).


We've made several tweaks to the container including (inspired from https://github.com/chris-crunchr/docker-st2-sso#introduction): 

1. simplifying the nginx proxy config - to just accepting http traffic from upstream oauth2 proxy
2. adding a bridge `auth.html` which retrieves a token (post request to /auth/tokens) and storing it in browser local storage before st2web starts 


## Limitations

we store the token in localstorage in the same exact object shape the st2web internals expect - with no compatibility guarantee. So if we upgrade, this is likely to break

We don't require CLI login so we've not setup uwsgi for st2-auth layer as suggested in  https://github.com/chris-crunchr/docker-st2-sso#introduction


There are several issues/PRs/projects on getting SSO native to stackstorm: 
- https://github.com/StackStorm/st2/issues/5625
- https://github.com/StackStorm/st2web/pull/983
- https://github.com/StackStorm/st2-auth-backend-sso-saml2

Once there's a clear docs on how to implement SSO we'll deprecate this and use that 