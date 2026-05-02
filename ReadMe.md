Renovation Project

## Property
**Peltheide 11, 3150 Haacht, Belgium**  
Detached split-level home (1968) · 3 bedrooms · EPC label F (708 kWh/m²·year) · plot 626 m²  
Source: [Dekrem Vastgoed listing](https://www.dekrem.be/pand-detail/verkoop-woning-haacht/7523708)

## Files
| File | Description |
|------|-------------|
| `property_data.json` | Full property details (address, rooms, energy data, legal obligations) |
| `renovation_agent.py` | Interactive AI renovation advisor pre-loaded with the property data |

## Usage

### 1. Install dependencies
```bash
pip install openai
```

### 2. Set your OpenAI API key
```bash
export OPENAI_API_KEY=sk-...
```

### 3. Run the agent
```bash
python renovation_agent.py
```

The agent will greet you with a summary of the property and wait for your renovation questions.  
Type `quit` to exit.

## Key renovation obligation
Under Flemish law, buyers must upgrade the property from **EPC label F → at least label D** within **6 years** of the notarial deed.  
Details: https://www.vlaanderen.be/een-huis-of-appartement-kopen/renovatieverplichting-voor-residentiele-gebouwen
