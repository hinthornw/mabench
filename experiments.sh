export LANGSMITH_PROJECT=daodejing

# Flat agent experiments:
# uv run --with-editable . python mabench/run.py --model "gpt-4o" --user-model "gpt-4o" --agent-strategy "single" --env "combined" --end-index 40 --max-concurrency 40 --n-distractors 0
# uv run --with-editable . python mabench/run.py --model "gpt-4o" --user-model "gpt-4o" --agent-strategy "single" --env "combined" --end-index 40 --max-concurrency 40 --n-distractors 1
# uv run --with-editable . python mabench/run.py --model "gpt-4o" --user-model "gpt-4o" --agent-strategy "single" --env "combined" --end-index 40 --max-concurrency 40 --n-distractors 2
# uv run --with-editable . python mabench/run.py --model "gpt-4o" --user-model "gpt-4o" --agent-strategy "single" --env "combined" --end-index 40 --max-concurrency 40 --n-distractors 4
# uv run --with-editable . python mabench/run.py --model "gpt-4o" --user-model "gpt-4o" --agent-strategy "single" --env "combined" --end-index 40 --max-concurrency 40 --n-distractors 6


# Supervisor. Need at least one distractor for it to actually be interesting

# uv run --with-editable . python mabench/run.py --model "gpt-4o" --user-model "gpt-4o" --agent-strategy "supervisor" --env "combined" --end-index 40 --max-concurrency 40 --n-distractors 1
uv run --with-editable . python mabench/run.py --model "gpt-4o" --user-model "gpt-4o" --remote --agent-strategy "supervisor" --env "combined" --end-index 40 --max-concurrency 40 --n-distractors 2
# uv run --with-editable . python mabench/run.py --model "gpt-4o" --user-model "gpt-4o" --agent-strategy "supervisor" --env "combined" --end-index 40 --max-concurrency 40 --n-distractors 4

find ./results -name "*.json" -exec stat -f "%m %N" {} + | sort -nr | cut -d' ' -f2- | while read file; do echo -n "$file: "; jq 'reduce .[] as $item ({"sum":0,"count":0}; .sum += $item.reward | .count += 1) | .sum / .count' "$file"; done
