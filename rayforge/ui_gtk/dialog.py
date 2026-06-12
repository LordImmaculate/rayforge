import logging
import sys
from typing import Callable, List, NotRequired, Optional, TypedDict

if sys.platform == "darwin":
    from AppKit import NSAlert, NSAlertStyleWarning

logger = logging.getLogger(__name__)


# Define a clean type structure for buttons
class DialogButton(TypedDict):
    id: str  # The string returned to your callback (e.g., 'save')
    label: str  # The text on the button (e.g., '_Save' or 'Cancel')
    is_default: NotRequired[bool]  # Triggered by Enter/Return key
    is_cancel: NotRequired[bool]  # Triggered by Escape key
    is_destructive: NotRequired[bool]  # Red styling in GTK


def show_platform_dialog(
    parent_window,
    heading: str,
    body: str,
    buttons: List[DialogButton],
    callback: Callable[[str], None],
    extra_child: Optional[object] = None,
):
    """
    Spawns a native NSAlert on macOS or an Adw.MessageDialog on Linux/Windows
    using a standardized button configuration array.

    Args:
        parent_window: The parent GTK window.
        heading: Dialog heading/title.
        body: Dialog body text.
        buttons: List of button configurations.
        callback: Called with the response id of the clicked button.
        extra_child: An optional GTK widget to embed in the dialog
                     (only shown on Linux/Windows; macOS NSAlert
                     does not support arbitrary extra widgets).
    """

    # ---------------------------------------------------------
    # macOS NATIVE IMPLEMENTATION
    # ---------------------------------------------------------
    if sys.platform == "darwin":
        if extra_child is not None:
            logger.debug(
                "Ignoring extra_child on macOS NSAlert for '%s'", heading
            )

        alert = NSAlert.alloc().init()
        alert.setMessageText_(heading)
        alert.setInformativeText_(body)
        alert.setAlertStyle_(NSAlertStyleWarning)

        # macOS prefers default/positive actions on the far right.
        # NSAlert appends buttons from right to left.
        # We sort buttons so default is first (far right), cancel is second, etc.
        sorted_buttons = sorted(
            buttons,
            key=lambda b: (
                not b.get("is_default", False),
                not b.get("is_cancel", False),
            ),
        )

        for btn_cfg in sorted_buttons:
            # Strip GTK underscores used for mnemonics (e.g., '_Save' -> 'Save')
            clean_label = btn_cfg["label"].replace("_", "")
            native_btn = alert.addButtonWithTitle_(clean_label)

            if btn_cfg.get("is_cancel", False):
                native_btn.setKeyEquivalent_("\x1b")  # Map Escape key

        response = alert.runModal()

        # NSAlert responses start at 1000 for the first added button, 1001 for the second...
        clicked_index = response - 1000
        if 0 <= clicked_index < len(sorted_buttons):
            callback(sorted_buttons[clicked_index]["id"])
        else:
            # Fallback to whichever button was marked as cancel
            cancel_id = next(
                (b["id"] for b in buttons if b.get("is_cancel")),
                buttons[-1]["id"],
            )
            callback(cancel_id)
        return

    # ---------------------------------------------------------
    # LINUX / WINDOWS GTK IMPLEMENTATION
    # ---------------------------------------------------------
    from gi.repository import Adw

    dialog = Adw.MessageDialog(
        transient_for=parent_window,
        heading=heading,
        body=body,
    )

    if extra_child is not None:
        dialog.set_extra_child(extra_child)

    default_id = None
    close_id = None

    for btn_cfg in buttons:
        b_id = btn_cfg["id"]
        dialog.add_response(b_id, btn_cfg["label"])

        if btn_cfg.get("is_default"):
            default_id = b_id
        if btn_cfg.get("is_cancel"):
            close_id = b_id

        if btn_cfg.get("is_destructive"):
            dialog.set_response_appearance(
                b_id, Adw.ResponseAppearance.DESTRUCTIVE
            )
        elif btn_cfg.get("is_default"):
            dialog.set_response_appearance(
                b_id, Adw.ResponseAppearance.SUGGESTED
            )

    if default_id:
        dialog.set_default_response(default_id)
    if close_id:
        dialog.set_close_response(close_id)

    def on_response(d, response_id):
        d.destroy()
        callback(response_id)

    dialog.connect("response", on_response)
    dialog.present()
