#!/bin/sh
old_po_dir="$1"
new_po_dir="$2"
pot="$3"
for old_po in "$old_po_dir"/*.po; do
    language="$(basename $old_po)"
    language=${language%%.po}
    new_po="$new_po_dir/$language.po"
    msgmerge "$old_po" "$pot" -o  "$new_po"
done
