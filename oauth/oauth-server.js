const express = require('express');
const OAuth2Server = require('oauth2-server');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// In-memory store for codes (for demo only)
const codes = {};

// Minimal /auth endpoint for authorization code flow
app.get('/auth', (req, res) => {
  const { response_type, client_id, redirect_uri, code_challenge, code_challenge_method, scope, state } = req.query;
  // For demo, auto-approve and issue a code
  const code = Math.random().toString(36).substring(2, 15);
  codes[code] = {
    client_id,
    redirect_uri,
    code_challenge,
    code_challenge_method,
    scope,
    // Add more as needed
  };
  // Redirect back to client with code (and state if present)
  let redirectUrl = `${redirect_uri}?code=${code}`;
  if (state) redirectUrl += `&state=${state}`;
  res.redirect(redirectUrl);
});

app.post('/register', (req, res) => {
  res.json({
    "client_id": "agent-1",
    "client_secret": "b1c2fb5c-5601-4a4f-89e2-e66707e7a4dd",
    "client_id_issued_at": 1718000000,
    "client_secret_expires_at": 0,
    "redirect_uris": ["http://localhost:9000/auth/callback"],
    "grant_types": ["client_credentials"]
  });
});

const Request = OAuth2Server.Request;
const Response = OAuth2Server.Response;

// In-memory model for demo purposes
const oauth = new OAuth2Server({
  model: {
    getClient: (clientId, clientSecret, cb) => {
      // Accept only agent-1 with the correct secret
      if (clientId === 'agent-1' && clientSecret === 'b1c2fb5c-5601-4a4f-89e2-e66707e7a4dd') {
        return cb(null, { id: clientId, grants: ['client_credentials', 'authorization_code'] });
      }
      cb(null, false);
    },
    saveToken: (token, client, user, cb) => {
      token.client = client;
      token.user = user;
      cb(null, token);
    },
    getUser: (username, password, cb) => cb(null, { id: username }),
    getAccessToken: (accessToken, cb) => cb(null, { accessToken, client: { id: 'agent-1' }, user: { id: 'user' }, accessTokenExpiresAt: new Date(Date.now() + 10000) }),
    // Add other required model methods as needed
  }
});

// Token endpoint
app.post('/token', (req, res) => {
  const request = new Request(req);
  const response = new Response(res);

  // If grant_type is authorization_code, validate the code
  if (req.body.grant_type === 'authorization_code') {
    const code = req.body.code;
    if (!codes[code]) {
      return res.status(400).json({ error: 'invalid_grant' });
    }
    // Optionally, check code_challenge, etc.
    // Remove the code after use
    delete codes[code];
    // Return a token
    return res.json({
      access_token: 'demo-access-token',
      token_type: 'Bearer',
      expires_in: 3600,
      scope: req.body.scope || 'openid profile email'
    });
  }

  // Otherwise, handle client_credentials as before
  oauth
    .token(request, response)
    .then(token => {
      res.json(token);
    })
    .catch(err => {
      res.status(err.code || 500).json(err);
    });
});

app.listen(3000, () => {
  console.log('OAuth2 provider listening on port 3000');
});