import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from data import traits, champions, composition_iterator

app = Flask(__name__)
app.secret_key = "gsdfkq34f89uu9FF9tr0ghs"


def timer(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        func()
        end = datetime.now()
        print(f"\n{func.__name__} execution takes {end - start}s.\n")

    return wrapper


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect("/")


@timer
def data_fill():
    for composition in composition_iterator:
        trait_champions = composition[0]
        trait_name = composition[1]
        for champion in trait_champions:
            champions[champion].append(trait_name)


@app.route("/", methods=["GET", "POST"])
def index():
    if "current_composition" not in session:
        session["current_composition"] = []
    if request.method == "POST":
        character = request.form["character"].lower()
        if character.capitalize() in session.get("current_composition", []):
            print(f"{character.capitalize()} already here")
        elif character.capitalize() == "help":
            return render_template(
                "index.html",
                composition=session["current_composition"],
                capped_traits=[],
                breakpoint_traits=[],
                remaining_traits=[],
                first_prior=[],
                second_prior=[],
                third_prior=[],
                no_prior=[],
                suggestions=None,
            )
        elif any(character == champ.lower() for champ in champions.keys()):
            if character.lower() not in [
                i.lower() for i in session["current_composition"]
            ]:
                session["current_composition"].append(character.capitalize())
                print(f"{character.capitalize()} has been added\n")
        else:
            print("Enter a valid character\n")
    group_data()
    suggestions = tailor()
    return render_template(
        "index.html",
        composition=session["current_composition"],
        capped_traits=session.get("capped_traits", []),
        breakpoint_traits=session.get("breakpoint_traits", []),
        remaining_traits=session.get("remaining_traits", []),
        first_prior=session.get("first_prior", []),
        second_prior=session.get("second_prior", []),
        third_prior=session.get("third_prior", []),
        no_prior=session.get("no_prior", []),
        suggestions=suggestions,
    )


def group_data():
    current_traits = {}
    capped_traits = []
    breakpoint_traits = []
    remaining_traits = []
    first_prior = []
    second_prior = []
    third_prior = []
    no_prior = []
    print("*" * 50, "\n")
    if not session["current_composition"]:
        return
    print(f"Your composition: {session['current_composition']}")
    for character in session["current_composition"]:
        for trait in champions[character]:
            current_traits[trait] = current_traits.get(trait, 0) + 1
    for trait, count in current_traits.items():
        if count == traits[trait][-1]:
            capped_traits.append(f"{trait}: {count} | CAPPED")
            no_prior.append(trait)
        elif count in traits[trait]:
            current_index = traits[trait].index(count)
            next_upgrade = traits[trait][current_index + 1] - count
            breakpoint_traits.append(
                f"{trait}: {count} | BREAKPOINT [+{next_upgrade}]")
            if next_upgrade == 1:
                first_prior.append(trait)
        else:
            remaining_traits.append(
                f"{trait}: {count} [+{traits[trait][0] - count}]")
            if (traits[trait][0] - count) == 1:
                second_prior.append(trait)
            if (traits[trait][0] - count) > 1:
                third_prior.append(trait)
    session["capped_traits"] = capped_traits
    session["breakpoint_traits"] = breakpoint_traits
    session["remaining_traits"] = remaining_traits
    session["first_prior"] = first_prior
    session["second_prior"] = second_prior
    session["third_prior"] = third_prior
    session["no_prior"] = no_prior


def tailor():
    first_prior = session.get("first_prior", [])
    second_prior = session.get("second_prior", [])
    third_prior = session.get("third_prior", [])
    no_prior = session.get("no_prior", [])
    suggestions = {
        name: 0
        for name in champions.keys()
        if name not in session.get("current_composition")
    }
    for i in session.get("current_composition", []):
        if i == "Akali k/da":
            champions["Akali true damage"] = []
        if i == "Akali true damage":
            champions["Akali k/da"] = []
    for trait in first_prior + second_prior + third_prior + no_prior:
        for name, traits in champions.items():
            if name not in session.get("current_composition", []):
                if trait in first_prior:
                    if trait in traits:
                        suggestions[name] += 3

                if trait in second_prior:
                    if trait in traits:
                        suggestions[name] += 2

                if trait in third_prior:
                    if trait in traits:
                        suggestions[name] += 1

                if trait in no_prior:
                    if trait in traits:
                        suggestions[name] += 0
    suggestions = dict(
        sorted(suggestions.items(), key=lambda item: item[1], reverse=True)
    )

    scoreboard = {}
    for character, score in suggestions.items():
        if score not in scoreboard:
            scoreboard[score] = [character]
        else:
            scoreboard[score].append(character)
    result = {}
    for score, characters in scoreboard.items():
        result[score] = characters
    return result


if __name__ == "__main__":
    data_fill()
    app.run(debug=False, host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)))
