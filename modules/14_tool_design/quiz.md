# Module 14 quiz

## 1. Does a six-tool catalog guarantee better accuracy?

<details>
<summary>Answer</summary>

No. Evaluate representative tasks with the same model, settings and budgets.

</details>

## 2. Why offer concise and detailed modes?

<details>
<summary>Answer</summary>

To return enough information for the current task without repeatedly sending unnecessary fields.

</details>

## 3. What does next_after mean?

<details>
<summary>Answer</summary>

Continue after the last returned stable ID; None means the end.

</details>

## 4. Why include a recovery action in an error?

<details>
<summary>Answer</summary>

It tells the model which valid next operation can supply missing information.

</details>

## 5. Are catalog characters equal to billed tokens?

<details>
<summary>Answer</summary>

No. Tokenizers differ, and provider wrappers add overhead.

</details>

## 6. What does the deterministic score prove?

<details>
<summary>Answer</summary>

The pipeline and scoring contract work; it does not measure an LLM.

</details>

## 7. Can a cached tool name authorize a call?

<details>
<summary>Answer</summary>

No. The execution boundary must recheck policy.

</details>
