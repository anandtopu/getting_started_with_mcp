# Module 16 quiz

## 1. Why namespace tools?

<details>
<summary>Answer</summary>

To prevent same-name tools from different servers being confused or shadowing each other.

</details>

## 2. Where does HTTP principal identity originate?

<details>
<summary>Answer</summary>

From a token whose signature, issuer, audience and required claims were verified.

</details>

## 3. Why recheck a previously visible tool?

<details>
<summary>Answer</summary>

Permissions or definitions may have changed since discovery.

</details>

## 4. What belongs in a private cache key?

<details>
<summary>Answer</summary>

Principal, effective permissions, policy version and relevant configuration.

</details>

## 5. Can a gateway forward the caller token to another API?

<details>
<summary>Answer</summary>

No. Obtain separate credentials intended for that upstream audience.

</details>

## 6. Do annotations enforce read-only behavior?

<details>
<summary>Answer</summary>

No. They are hints; reviewed implementation and runtime policy enforce boundaries.

</details>

## 7. When should servers stay separate?

<details>
<summary>Answer</summary>

When they have different owners, credentials, deployment schedules or failure domains.

</details>
