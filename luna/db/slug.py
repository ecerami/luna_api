"""Slug Utilities."""
import re
import os


class SlugUtil:
    """Slug Utilities."""

    def sluggify(self, str):
        """Sluggify the specified string."""
        # In case we receive a file name with extension, remove the extension
        if "." in str:
            str = os.path.splitext(str)[0]

        # Replace dashes with underscores
        slug = str.replace("-", "_")

        # Remove all non-word characters
        slug = re.sub(r"[^\w\s]", "", slug)

        # Replace all runs of dash or whitespace with a single dash
        slug = re.sub(r"_+", "_", slug)
        slug = re.sub(r"\s+", "_", slug)

        slug = slug.lower()
        return slug
