# Helpers

Utility functions and constants for use in your RickBot cogs.

## Built-in Helpers

### `colors.py`
Embed color constants:
- `MAIN_EMBED_COLOR` - Primary purple color
- `ERROR_EMBED_COLOR` - Error red color
- `SUCCESS_EMBED_COLOR` - Success green color

```python
from helpers.colors import MAIN_EMBED_COLOR
import discord

embed = discord.Embed(
    title="Hello",
    description="World",
    color=MAIN_EMBED_COLOR
)
```

## Custom Helpers

Add your own utility functions in the `custom/` folder:

```python
# helpers/custom/my_utils.py

async def my_helper_function(ctx, arg):
    """Your custom helper"""
    # Your code here
    pass
```

Then import in your cogs:

```python
from helpers.custom.my_utils import my_helper_function
```
