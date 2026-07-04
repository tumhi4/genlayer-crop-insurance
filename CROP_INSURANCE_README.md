# Parametric Crop Insurance using Local Weather News

An Intelligent Contract primitive built on **GenLayer** that automates crop insurance payouts. Farmers lock in policies specifying their crop, location, and a trusted local weather news source. GenLayer validators automatically crawl reports and verify weather disasters (frost, flood, drought) to trigger instant payouts.

---

## 📖 How It Works
1. **Policy Registration**: The insurer registers a policy with farmer details, crop type, location, and the weather bulletin source URL.
2. **Evaluation**: When a weather disaster occurs, anyone can trigger `evaluate_policy_claim`.
3. **Automated Audit**: GenLayer validators crawl the news site or report page content using `gl.nondet.web.render`.
4. **Resolution**: Validator LLMs analyze the report text against the policy's location and crop type. If a qualifying disaster is found, consensus verifies it and updates the policy status to `PAID_OUT`.

---

## ⚙️ Lifecycle States
```
[ ACTIVE ] ──(evaluate_policy_claim)──▶ [ LLM Weather Audit ] ──(Consensus: True)──▶ [ PAID_OUT ]
                                               │
                                               └──(Consensus: False)──▶ [ Revert Transaction ]
```

---

## 🛠️ Key Technical Features
*   **Web Scraping integration**: Uses `gl.nondet.web.render(url, mode="text")` to fetch the news reports dynamically inside non-deterministic execution blocks.
*   **Consensus Optimization**: The LLM prompt asks for both reasoning and a boolean trigger status, but the contract extracts and checks **only the raw boolean string** (`"True"` or `"False"`) inside the non-deterministic block. This prevents validator disagreement on subjective text explanations, ensuring single-round consensus.
*   **Case-Insensitive Normalization**: Automatically normalizes developer and farmer addresses to prevent EIP-55 checksum case mismatch errors.
*   **Tokenless & Sandbox Friendly**: Supports `premium/payout >= 0` parameters to allow testing in 0-token localnet and testnet environments.

---

## 🚀 How to Test in GenLayer Studio

### 1. Deployment
Deploy the contract using:
*   **`owner`**: Paste your active GenLayer account address.

### 2. Create a Policy
*   Call `create_policy()` with:
    *   `farmer`: Paste your active GenLayer account address (or a second address).
    *   `location`: `"Mendoza, Argentina"`
    *   `crop_type`: `"Grapes"`
    *   `news_source_url`: Paste a Gist URL containing weather text.
    *   `premium`: `0`
    *   `payout_amount`: `0`
*   *Result*: Generates a policy ID (e.g. `"POLICY_1"`).

### 3. Trigger Claim Evaluation
*   Create a raw text snippet (e.g., via a public GitHub Gist) containing the simulated weather report:
    ```
    MENDOZA, ARGENTINA — A severe and unexpected late frost swept across the Mendoza wine region yesterday, destroying over 40% of local Grape crops.
    ```
*   Call `evaluate_policy_claim()` with:
    *   `policy_id`: `"POLICY_1"`
*   *Result*: The validator network evaluates the weather text and finalizes the transaction with **SUCCESS** in a single round, transitioning the status to `"PAID_OUT"`.
