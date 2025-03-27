from langchain.chat_models import init_chat_model

import argparse

from mabench.environments import EnvProtocol
from langgraph.checkpoint.memory import InMemorySaver
from mabench.agents.supervisor import create_supervisor


def create_single_agent(
    wiki: str, model: str, tools: list, checkpointer: InMemorySaver | bool, name: str
):
    from langgraph.prebuilt import create_react_agent

    prompt = f"""You are a helpful support assistant.

In assisting the user, please comply with the following policies.

{wiki}

# Instruction
You need to act as an agent that use your tools to help the user according to the above policy.
Try to be helpful and always follow the policy."""  # noqa: E501

    print(f"Constructing agent {name} with {len(tools)} tools")
    agent = create_react_agent(
        model=model,
        prompt=prompt,
        tools=tools,
        checkpointer=checkpointer,
        name=name.replace(" ", "_").lower().strip(),
    )
    return agent


def create_hierarchy(env: EnvProtocol, model: str):

    environments = env.environments
    checkpointer = InMemorySaver()
    agents = []
    for environment in environments:
        agents.append(
            create_single_agent(
                environment.wiki,
                model,
                list(environment.tools_map.values()),
                True,
                name=f"{environment.name}_agent".lower().replace(" ", "_").strip(),
            )
        )

    workflow = create_supervisor(
        agents,
        model=init_chat_model(model),
        prompt=(
            """You are a customer support assistant tasked with helping users.

# Instructions

You need to act as a supervisor, routing work to the appropriate agent to take actions or retrieve knowledge. When the agents are finished, they will report back to you with the answer, confirmation of completion, or an error if they run into an issue. 

You interface with the user. The agents reporting to you cannot. If the other agents have questions or issues, they need you to answer them or relay the information to the user. The user needn't know about the presence of the other agents. You are accountable for the ultimate success of the interaction, including confirmation with your reports around task completion.
Use all resources available to enable a successful interaction."""
        ),
        supervisor_name="support_supervisor",
        handoff_prefix="assign_to_",
        include_agent_name="inline",
    )
    return workflow.compile(checkpointer=checkpointer, name="Support Supervisor")


def agent_factory(env: EnvProtocol, agent_strategy: str, model: str):
    if isinstance(env, str):
        raise ValueError("Environment must be an EnvProtocol, not a string")
    if agent_strategy == "single":
        return create_single_agent(
            env.wiki,
            model,
            list(env.tools_map.values()),
            InMemorySaver(),
            name="Support Agent",
        )

    elif agent_strategy == "supervisor":
        return create_hierarchy(env, model)
    elif agent_strategy == "swarm":
        raise NotImplementedError(f"Agent strategy {agent_strategy} not implemented")

    else:
        raise ValueError(f"Unknown agent strategy: {agent_strategy}")
