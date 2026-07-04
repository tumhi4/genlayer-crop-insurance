# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
import json
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class Policy:
    id: str
    farmer: str
    location: str
    crop_type: str
    news_source_url: str
    premium: u256
    payout_amount: u256
    status: str  # "ACTIVE" | "PAID_OUT" | "EXPIRED"


class CropInsurance(gl.Contract):
    owner: str
    policies: TreeMap[str, Policy]
    next_policy_id: u256

    def __init__(self, owner: str):
        self.owner = owner.lower()
        self.policies = TreeMap()
        self.next_policy_id = u256(0)

    @gl.public.write
    def create_policy(
        self,
        farmer: str,
        location: str,
        crop_type: str,
        news_source_url: str,
        premium: int,
        payout_amount: int
    ) -> str:
        # Access control: only owner/insurer can issue policies
        sender = str(gl.message.sender_address).lower()
        assert sender == self.owner, "Only the owner can create policies."
        assert premium >= 0, "Premium must be zero or greater."
        assert payout_amount >= 0, "Payout amount must be zero or greater."

        # Increment policy ID
        policy_num = int(self.next_policy_id) + 1
        self.next_policy_id = u256(policy_num)
        policy_id = "POLICY_" + str(policy_num)

        # Initialize and store policy
        new_policy = Policy(
            id=policy_id,
            farmer=farmer.lower(),
            location=location,
            crop_type=crop_type,
            news_source_url=news_source_url,
            premium=u256(premium),
            payout_amount=u256(payout_amount),
            status="ACTIVE"
        )
        self.policies[policy_id] = new_policy
        return policy_id

    @gl.public.write
    def evaluate_policy_claim(self, policy_id: str) -> None:
        assert policy_id in self.policies, "Policy does not exist."
        
        policy = self.policies[policy_id]
        assert policy.status == "ACTIVE", "Policy is not active."

        # Local snapshots for non-deterministic execution block
        loc = policy.location
        crop = policy.crop_type
        url = policy.news_source_url

        # Zero-argument closure for web crawling and LLM verification
        def check_weather_news():
            # 1. Fetch local weather/news report text
            web_data = gl.nondet.web.render(url, mode="text")

            # 2. Instruct the LLM to analyze the weather impact
            prompt = (
                "You are an automated parametric insurance assessor.\n"
                "Review the following news/meteorological report and determine if a qualifying severe weather event "
                "(e.g., drought, flood, frost, extreme heat, hail) has damaged or destroyed crops in the specified area.\n\n"
                "## Target Location:\n"
                + loc + "\n\n"
                "## Target Crop Type:\n"
                + crop + "\n\n"
                "## Weather Reports / News Text:\n"
                + web_data + "\n\n"
                "## Output Requirements:\n"
                "Output must be in JSON format:\n"
                "{\n"
                "  \"is_triggered\": true/false,\n"
                "  \"reasoning\": \"a brief explanation referencing weather facts in the text\"\n"
                "}\n"
                "Respond ONLY with raw JSON."
            )
            response = gl.nondet.exec_prompt(prompt, response_format="json")
            
            # Extract only the boolean trigger status to ensure instant consensus
            is_triggered = bool(response.get("is_triggered", False))
            return str(is_triggered)

        # Run under strict equality consensus matching
        consensus_result = gl.eq_principle.strict_eq(check_weather_news)

        # Payout validation check
        assert consensus_result == "True", "Consensus rejected the claim: no qualifying weather disaster found."

        # Update policy status to paid out
        policy.status = "PAID_OUT"
        self.policies[policy_id] = policy

    @gl.public.view
    def get_policy(self, policy_id: str) -> Policy:
        return self.policies[policy_id]

    @gl.public.view
    def get_total_policies(self) -> u256:
        return self.next_policy_id
