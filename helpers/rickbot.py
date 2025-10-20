"""
This is a helper file for the RickBot ASCII art.

Please do not change the art, or remove it, it will make me sad.
"""

# Import the required modules

# Third-party Modules
# -------------------
from termcolor import (
    colored,
)  # Termcolor is used to add color to terminal text, enhancing the readability of console outputs.

# Constants
# ---------

# This constant contains the ASCII art that is printed to the console when RickBot starts.
# The art is a stylized version of RickBot's name, created using text with colored attributes.
START_SUCCESS_RICKBOT_ART = (
    str(
        """
    {0}        {1}
   {2}     {3}
  {4}     {5}
 {6}   {7}
{8} {9}
""".format(
            colored("//   ) )               //", "magenta", attrs=["bold"]),
            colored("//   ) )", "cyan", attrs=["bold"]),
            colored("//___/ /  ( )  ___     //___", "magenta", attrs=["bold"]),
            colored("//___/ /   ___    __  ___", "cyan", attrs=["bold"]),
            colored("/ ___ (   / / //   ) ) //\\ \\", "magenta", attrs=["bold"]),
            colored("/ __  (   //   ) )  / /", "cyan", attrs=["bold"]),
            colored("//   | |  / / //       //  \\ \\", "magenta", attrs=["bold"]),
            colored("//    ) ) //   / /  / /", "cyan", attrs=["bold"]),
            colored("//    | | / / ((____   //    \\ \\", "magenta", attrs=["bold"]),
            colored("//____/ / ((___/ /  / /", "cyan", attrs=["bold"]),
        )
    )
    + "                      "
    + colored("RickBot:", "magenta", attrs=["bold"])
    + " "
    + colored("Ready!", "green", attrs=["bold"])
    + "\n"
)


def get_goodbye_message() -> str:
    """
    Get a colorful goodbye message for shutdown.

    Returns:
        Formatted goodbye message
    """
    return (
        colored("RickBot", "magenta", attrs=["bold"])
        + " says "
        + colored("goodbye!", "cyan", attrs=["bold"])
    )
