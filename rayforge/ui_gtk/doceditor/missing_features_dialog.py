from gettext import gettext as _
from typing import Set

from gi.repository import Gtk

from ..dialog import show_platform_dialog


def show_missing_features_dialog(parent: Gtk.Window, missing_types: Set[str]):
    """
    Show a dialog informing the user about missing features.

    This happens when a document contains steps whose producer types
    are not registered (e.g., because the addon providing them is not
    installed).
    """
    if len(missing_types) == 1:
        msg = _(
            "This document uses a feature that is not available: {}"
        ).format(list(missing_types)[0])
    else:
        types_list = ", ".join(sorted(missing_types))
        msg = _(
            "This document uses features that are not available: {}"
        ).format(types_list)

    msg += "\n\n" + _("The document can still be edited and saved.")

    show_platform_dialog(
        parent_window=parent,
        heading=_("Missing Features"),
        body=msg,
        buttons=[{"id": "ok", "label": _("_OK")}],
        callback=lambda response_id: None,
    )
