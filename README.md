# AI Test Case Generation and Browser Automation

Small Python examples for generating login test cases with an OpenAI-compatible chat API and driving a browser from JSON test steps. The examples use a SauceDemo login page and support Groq, OpenAI, Gemini, and Ollama for text generation. Browser execution is set to Playwright by default, with an alternate Selenium implementation.

## Project Files

- `Scripts/firstBasicPrompt.py` sends two prompts and prints generated test cases.
- `Scripts/twoJsonOutput.py` requests positive, negative, and boundary cases as JSON, prints the parsed cases, and writes `test_suite.json`.
- `Scripts/thirdHybridFw.py` loads `test_suite.json` and `step_map.json`, maps test steps to browser actions, and runs them with Playwright or Selenium.
- `Scripts/step_map.json` maps normalized phrases to navigation, form-fill, and click actions on SauceDemo.
- `Scripts/test_suite.json` is a sample structured login test suite used by the browser runner.
- `Scripts/Test.py` is a standalone API-call example. It currently contains a hard-coded API credential; do not run or share it until that credential has been revoked and removed.

## Setup

Use Python 3.13 or another version supported by the dependencies. From the project directory, create and activate a virtual environment, then install the packages for the examples you intend to run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install openai python-dotenv playwright
python -m playwright install chromium
```

For the Selenium option, install its additional packages:

```powershell
python -m pip install selenium webdriver-manager
```

Selenium also requires a compatible Chrome installation. `webdriver-manager` downloads the matching driver when the script runs.

## API Configuration

Set the API key for the provider selected by the `PROVIDER` variable in the script. The current examples read these environment variable names:

| Provider | Environment variable | Notes |
| --- | --- | --- |
| Groq | `my_API_KEY` | Current default in the generation scripts. |
| OpenAI | `OPENAI_API_KEY` | Uses the OpenAI API. |
| Gemini | `GEMINI_API_KEY` | Uses Gemini's OpenAI-compatible endpoint. |
| Ollama | None | Requires Ollama running locally with the configured model available. |

The scripts call `load_dotenv()`, so a `.env` file in the current working directory can supply the selected variable. Keep API keys out of source files and version control. Revoke any credential that has been committed or otherwise exposed.

## Run the Examples

Run commands from `Scripts` because the scripts read and write JSON files using paths relative to the current working directory:

```powershell
Set-Location .\Scripts
python .\firstBasicPrompt.py
python .\twoJsonOutput.py
python .\thirdHybridFw.py
```

Run `twoJsonOutput.py` before `thirdHybridFw.py` to generate a fresh test suite. The browser runner can also use the included sample `test_suite.json`. To switch browser drivers, change `FRAMEWORK` in `thirdHybridFw.py` to `"selenium"` or `"playwright"`.

## Current Limitations

- Generated test steps must match entries in `step_map.json` after normalization; unmapped steps are skipped with a warning.
- The browser runner performs navigation, fill, and click actions, then prints each expected result. It does not check the page for that result or report a pass/fail assertion.
- Playwright currently launches Chromium in headed mode, so a browser window opens during execution.
- Provider and model names are configured directly in the Python scripts.
