from random import choice

from django import forms
from django.shortcuts import render, redirect
from markdown2 import Markdown

from . import util


class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Enter the title"}
    ), label="Title")
    content = forms.CharField(widget=forms.Textarea(), label="Content")


class EntryEditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(), label="Content")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entries = util.list_entries()

    if title not in entries:
        return render(request, "encyclopedia/error.html", {
            "code": "404: Not Found",
            "message": "Requested page not found."
        }, status=404)

    markdowner = Markdown()
    content = markdowner.convert(util.get_entry(title))

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content
    })


def search(request):
    entries = util.list_entries()

    query = request.GET.get("q")

    if query in entries:
        return redirect(f"/wiki/{query}")

    results = []

    for entry in entries:
        if query.lower() in entry.lower():
            results.append(entry)

    length = len(results)

    return render(request, "encyclopedia/search.html", {
        "results": results,
        "length": length
    })


def new(request):
    if request.method == "POST":      
        form = NewEntryForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            entries = util.list_entries()

            if title in entries:
                return render(request, "encyclopedia/error.html", {
                    "code": "409: Conflict",
                    "message": "Page with the same title already exists. Please try a different title."
                }, status=409)

            util.save_entry(title, content)

            return redirect(f"/wiki/{title}")
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form
            })

    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm()
    })


def edit(request, title):
    if request.method == "POST":
        form = EntryEditForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data["content"]

            util.save_entry(title, content)

            return redirect(f"/wiki/{title}")
        else:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "form": form
            })

    entries = util.list_entries()

    if title not in entries:
        return render(request, "encyclopedia/error.html", {
            "code": "404: Not Found",
            "message": "Page not found!"
        })

    entry = util.get_entry(title)

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": EntryEditForm(initial={"content": entry })
    })


def random(request):
    entries = util.list_entries()
    random_entry = choice(entries)

    return redirect(f"/wiki/{random_entry}")
