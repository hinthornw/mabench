# Adapted from τ-bench https://arxiv.org/abs/2406.12045 by Sierra
import langsmith as ls
import uuid
from mabench.environments.base import Env
from mabench.bench_types import (
    SolveResult,
)
from typing import Optional

import os
import json
import random
import argparse
import traceback
from math import comb
import multiprocessing
from datetime import datetime
from typing import List
from concurrent.futures import ThreadPoolExecutor

from mabench.environments import get_env, EnvProtocol
from mabench.bench_types import EnvRunResult
from mabench.environments.user import UserStrategy
from langgraph.graph.state import CompiledStateGraph


def run(
    args: argparse.Namespace,
    ckpt_path: str,
) -> List[EnvRunResult]:
    print(f"Loading user with strategy: {args.user_strategy}")
    env = get_env(
        args.env,
        user_strategy=args.user_strategy,
        user_model=args.user_model,
        user_provider=args.user_model_provider,
        task_split=args.task_split,
    )
    agent = agent_factory(
        env=env,
        args=args,
    )
    end_index = (
        len(env.tasks) if args.end_index == -1 else min(args.end_index, len(env.tasks))
    )
    results: List[EnvRunResult] = []
    lock = multiprocessing.Lock()
    if args.task_ids and len(args.task_ids) > 0:
        print(f"Running tasks {args.task_ids} (checkpoint path: {ckpt_path})")
    else:
        print(
            f"Running tasks {args.start_index} to {end_index} (checkpoint path: {ckpt_path})"
        )
    for i in range(args.num_trials):
        if args.task_ids and len(args.task_ids) > 0:
            idxs = args.task_ids
        else:
            idxs = list(range(args.start_index, end_index))
        if args.shuffle:
            random.shuffle(idxs)

        @ls.traceable(name="Run Experiment")
        def _run(idx: int) -> EnvRunResult:
            isolated_env = get_env(
                args.env,
                user_strategy=args.user_strategy,
                user_model=args.user_model,
                task_split=args.task_split,
                user_provider=args.user_model_provider,
                task_index=idx,
            )

            print(f"Running task {idx}")
            try:
                res = solve(
                    agent,
                    env=isolated_env,
                    task_index=idx,
                )
                result = EnvRunResult(
                    task_id=idx,
                    reward=res.reward,
                    info=res.info,
                    traj=res.messages,
                    trial=i,
                )
            except Exception as e:
                ls.get_current_run_tree().error = repr(e)
                result = EnvRunResult(
                    task_id=idx,
                    reward=0.0,
                    info={"error": str(e), "traceback": traceback.format_exc()},
                    traj=[],
                    trial=i,
                )
            print(
                "✅" if result.reward == 1 else "❌",
                f"task_id={idx}",
                result.info,
            )
            print("-----")
            with lock:
                data = []
                if os.path.exists(ckpt_path):
                    with open(ckpt_path, "r") as f:
                        data = json.load(f)
                with open(ckpt_path, "w") as f:
                    json.dump(data + [result.model_dump()], f, indent=2)
            return result

        with ThreadPoolExecutor(max_workers=args.max_concurrency) as executor:
            res = list(executor.map(_run, idxs))
            results.extend(res)

    return results


def agent_factory(env: EnvProtocol, args: argparse.Namespace):
    if args.agent_strategy == "single":
        from langgraph.prebuilt import create_react_agent
        from langgraph.checkpoint.memory import InMemorySaver

        prompt = f"""You are a helpful support assistant. In assisting the user, please comply with the following policies.

{env.wiki}"""  # noqa: E501

        agent = create_react_agent(
            model=args.model,
            prompt=prompt,
            tools=list(env.tools_map.values()),
            checkpointer=InMemorySaver(),
        )
        agent.name = "Support Agent"
        return agent
    else:
        raise ValueError(f"Unknown agent strategy: {args.agent_strategy}")


def display_metrics(results: List[EnvRunResult]) -> None:
    def is_successful(reward: float) -> bool:
        return (1 - 1e-6) <= reward <= (1 + 1e-6)

    num_trials = len(set([r.trial for r in results]))
    rewards = [r.reward for r in results]
    avg_reward = sum(rewards) / len(rewards)
    # c from https://arxiv.org/pdf/2406.12045
    c_per_task_id: dict[int, int] = {}
    for result in results:
        if result.task_id not in c_per_task_id:
            c_per_task_id[result.task_id] = 1 if is_successful(result.reward) else 0
        else:
            c_per_task_id[result.task_id] += 1 if is_successful(result.reward) else 0
    pass_hat_ks: dict[int, float] = {}
    for k in range(1, num_trials + 1):
        sum_task_pass_hat_k = 0
        for c in c_per_task_id.values():
            sum_task_pass_hat_k += comb(c, k) / comb(num_trials, k)
        pass_hat_ks[k] = sum_task_pass_hat_k / len(c_per_task_id)
    print(f"🏆 Average reward: {avg_reward}")
    print("📈 Pass^k")
    for k, pass_hat_k in pass_hat_ks.items():
        print(f"  k={k}: {pass_hat_k}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-trials", type=int, default=1)
    parser.add_argument(
        "--env", type=str, choices=["retail", "airline", "combined"], default="retail"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="The model to use for the agent",
    )
    parser.add_argument(
        "--model-provider",
        type=str,
        help="The model provider for the agent",
    )
    parser.add_argument(
        "--user-model",
        type=str,
        default="gpt-4o",
        help="The model to use for the user simulator",
    )
    parser.add_argument(
        "--user-model-provider",
        type=str,
        help="The model provider for the user simulator",
    )
    parser.add_argument(
        "--agent-strategy",
        type=str,
        default="tool-calling",
        choices=["single"],
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="The sampling temperature for the action model",
    )
    parser.add_argument(
        "--task-split",
        type=str,
        default="test",
        choices=["train", "test", "dev"],
        help="The split of tasks to run (only applies to the retail domain for now",
    )
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--end-index", type=int, default=-1, help="Run all tasks if -1")
    parser.add_argument(
        "--task-ids",
        type=int,
        nargs="+",
        help="(Optional) run only the tasks with the given IDs",
    )
    parser.add_argument("--log-dir", type=str, default="results")
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=1,
        help="Number of tasks to run in parallel",
    )
    parser.add_argument("--seed", type=int, default=10)
    parser.add_argument("--shuffle", type=int, default=0)
    parser.add_argument(
        "--user-strategy",
        type=str,
        default="llm",
        choices=[item.value for item in UserStrategy],
    )
    parser.add_argument(
        "--few-shot-displays-path",
        type=str,
        help="Path to a jsonlines file containing few shot displays",
    )
    args = parser.parse_args()
    print(args)
    random.seed(args.seed)

    time_str = datetime.now().strftime("%m%d%H%M%S")
    file_str = f"{args.log_dir}/{args.agent_strategy}-{args.model.split('/')[-1]}-{args.temperature}_range_{args.start_index}-{args.end_index}_user-{args.user_model}-{args.user_strategy}_{time_str}.json"

    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir)

    results = run(
        args=args,
        ckpt_path=file_str,
    )

    display_metrics(results)

    with open(file_str, "w") as f:
        json.dump([result.model_dump() for result in results], f, indent=2)
        print(f"\n📄 Results saved to {file_str}\n")


@ls.traceable(name="Solve")
def solve(
    agent: CompiledStateGraph,
    env: Env,
    task_index: Optional[int] = None,
    max_num_turns: int = 10,
) -> SolveResult:
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    response = env.reset(task_index=task_index)
    reward = 0.0
    next_message = {"role": "user", "content": response.observation}
    info = {}
    for _ in range(max_num_turns):
        new_state = agent.invoke({"messages": [next_message]}, config)
        env_response = env.step(new_state["messages"])
        obs = env_response.observation
        reward = env_response.reward
        info = {**info, **env_response.info.model_dump()}
        if env_response.done:
            break
        next_message = {"role": "user", "content": obs}
        if env_response.done:
            break
    state = agent.get_state(config)
    messages = state.values["messages"]

    return SolveResult(
        messages=messages,
        reward=reward,
        info=info,
    )


if __name__ == "__main__":
    main()
