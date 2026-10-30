# Quiz

### 1. Who issues the access token?

<details>
<summary>Answer</summary>

The authorization server. The MCP resource server verifies it; the host obtains it on behalf of the user.

</details>

### 2. Does a valid signature make a token usable everywhere?

<details>
<summary>Answer</summary>

No. The configured issuer, intended audience, expiry, required claims and operation scopes must also pass.

</details>

### 3. What does PKCE bind?

<details>
<summary>Answer</summary>

The code exchange to the verifier held by the client that initiated this authorization. The S256 challenge alone cannot redeem the code.

</details>

### 4. Why keep state and issuer with the pending redirect?

<details>
<summary>Answer</summary>

State correlates the browser response to one local attempt; the recorded issuer prevents accepting an authorization response from another authority.

</details>

### 5. When is pre-registration appropriate?

<details>
<summary>Answer</summary>

When client and identity provider already have a relationship, as in this local Keycloak realm. A new public deployment can use a hosted HTTPS Client ID Metadata Document when supported.

</details>

### 6. What happens when a read token attempts a write?

<details>
<summary>Answer</summary>

The HTTP gate returns 403 insufficient_scope with the required scope set. The SDK can obtain additional consent, union scopes and retry; the tool still requires host approval.

</details>

### 7. Why is an in-memory authorization test insufficient?

<details>
<summary>Answer</summary>

It bypasses HTTP bearer middleware. The lesson tests the resource server through actual loopback HTTP.

</details>
