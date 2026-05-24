#!/usr/bin/env bash
# Wiki Ingest Quality Evaluator
# Runs LLM-as-judge evaluation against golden samples
#
# Requirements:
#   - ANTHROPIC_API_KEY environment variable set
#   - jq installed (brew install jq)
#   - curl installed
#
# Usage:
#   ./run-eval.sh                    # Run all samples
#   ./run-eval.sh cursor             # Run specific sample
#   ./run-eval.sh --model opus       # Use different judge model

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="${SCRIPT_DIR}/results"
SAMPLES_DIR="${SCRIPT_DIR}/samples"
RUBRIC="${SCRIPT_DIR}/rubric.md"
JUDGE_PROMPT="${SCRIPT_DIR}/judge-prompt.md"
MODEL="claude-sonnet-4-6"
API_URL="https://api.anthropic.com/v1/messages"

# Parse arguments
SAMPLE_FILTER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="$2"
      shift 2
      ;;
    *)
      SAMPLE_FILTER="$1"
      shift
      ;;
  esac
done

# Check prerequisites
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "Error: ANTHROPIC_API_KEY environment variable not set"
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed"
  exit 1
fi

# Create results directory
mkdir -p "${RESULTS_DIR}"

# Read rubric and judge prompt
RUBRIC_CONTENT=$(cat "${RUBRIC}")
JUDGE_PROMPT_CONTENT=$(cat "${JUDGE_PROMPT}")

# Find samples
SAMPLES=()
for input_file in "${SAMPLES_DIR}/input/"*.md; do
  [[ -f "$input_file" ]] || continue
  sample_name=$(basename "$input_file" .md)
  if [[ -n "$SAMPLE_FILTER" && "$sample_name" != "$SAMPLE_FILTER" ]]; then
    continue
  fi
  SAMPLES+=("$sample_name")
done

if [[ ${#SAMPLES[@]} -eq 0 ]]; then
  echo "No samples found matching filter: ${SAMPLE_FILTER:-all}"
  exit 1
fi

echo "Running eval with model: ${MODEL}"
echo "Samples: ${SAMPLES[*]}"
echo "---"

# Run evaluation for each sample
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ALL_SCORES=()

for sample in "${SAMPLES[@]}"; do
  echo "Evaluating: ${sample}"

  INPUT_FILE="${SAMPLES_DIR}/input/${sample}.md"
  EXPECTED_FILE="${SAMPLES_DIR}/expected/${sample}-entity.md"

  if [[ ! -f "$EXPECTED_FILE" ]]; then
    echo "  Skipping: no expected output file at ${EXPECTED_FILE}"
    continue
  fi

  INPUT_CONTENT=$(cat "$INPUT_FILE")
  EXPECTED_CONTENT=$(cat "$EXPECTED_FILE")

  # For actual output, we use the existing wiki entity page if it exists
  # Otherwise, the user must generate it first by running wiki-ingest
  ACTUAL_FILE="${SCRIPT_DIR}/../../data/wiki/entities/${sample}.md"
  if [[ ! -f "$ACTUAL_FILE" ]]; then
    echo "  Skipping: no actual output file at ${ACTUAL_FILE}"
    echo "  Run wiki-ingest on this source first, then re-run eval"
    continue
  fi
  ACTUAL_CONTENT=$(cat "$ACTUAL_FILE")

  # Build the judge request
  JUDGE_USER_CONTENT=$(cat <<HEREDOC
## Rubric

${RUBRIC_CONTENT}

## Raw Source

${INPUT_CONTENT}

## Expected Output (Golden Sample)

${EXPECTED_CONTENT}

## Actual Output (To Evaluate)

${ACTUAL_CONTENT}
HEREDOC
)

  # Call Claude API
  RESPONSE=$(curl -s "${API_URL}" \
    -H "Content-Type: application/json" \
    -H "x-api-key: ${ANTHROPIC_API_KEY}" \
    -H "anthropic-version: 2023-06-01" \
    -d "$(jq -n \
      --arg model "$MODEL" \
      --arg system "$JUDGE_PROMPT_CONTENT" \
      --arg user "$JUDGE_USER_CONTENT" \
      '{
        model: $model,
        max_tokens: 1024,
        system: $system,
        messages: [{role: "user", content: $user}]
      }')")

  # Extract the score JSON from the response
  SCORE_TEXT=$(echo "$RESPONSE" | jq -r '.content[0].text // empty')

  if [[ -z "$SCORE_TEXT" ]]; then
    echo "  Error: no response from API"
    echo "  Response: $(echo "$RESPONSE" | jq -c '.error // .')"
    continue
  fi

  # Try to parse as JSON (the model should return JSON)
  SCORE_JSON=$(echo "$SCORE_TEXT" | jq '.' 2>/dev/null || echo "null")

  if [[ "$SCORE_JSON" == "null" ]]; then
    # Try to extract JSON from markdown code block
    SCORE_JSON=$(echo "$SCORE_TEXT" | sed -n '/```json/,/```/p' | head -n -1 | tail -n +2 | jq '.' 2>/dev/null || echo "null")
  fi

  # Save individual result
  RESULT_FILE="${RESULTS_DIR}/${sample}-${TIMESTAMP}.json"
  echo "$SCORE_JSON" > "$RESULT_FILE"

  # Display score
  if [[ "$SCORE_JSON" != "null" ]]; then
    TOTAL=$(echo "$SCORE_JSON" | jq -r '.weighted_total // "N/A"')
    PASS=$(echo "$SCORE_JSON" | jq -r '.pass // "N/A"')
    echo "  Score: ${TOTAL}/5.0 | Pass: ${PASS}"
    ALL_SCORES+=("$TOTAL")
  else
    echo "  Error: could not parse score JSON"
    echo "  Raw response saved to ${RESULT_FILE}"
  fi
done

# Summary
echo "---"
echo "Results saved to: ${RESULTS_DIR}/"
if [[ ${#ALL_SCORES[@]} -gt 0 ]]; then
  AVG=$(echo "${ALL_SCORES[@]}" | awk '{s=0; for(i=1;i<=NF;i++) s+=$i; print s/NF}')
  echo "Average score: ${AVG}/5.0"
  echo "Passing threshold: 3.5/5.0"
fi
