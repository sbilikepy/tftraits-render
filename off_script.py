from datetime import datetime

from data import traits, champions, composition_iterator

current_composition = []
current_traits = {}
capped_traits = []
breakpoint_traits = []
remaining_traits = []
first_prior = []
second_prior = []
third_prior = []
no_prior = []


def timer(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        func()
        end = datetime.now()
        print(f"\n{func.__name__} execution takes {end - start}s.\n")

    return wrapper


@timer
def data_fill():
    for composition in composition_iterator:
        trait_champions = composition[0]
        trait_name = composition[1]
        for champion in trait_champions:
            champions[champion].append(trait_name)


@timer
def request():
    print('Enter "help" to calculate')

    flag = True
    while flag:
        character = input("Character name: ").lower()
        if character.capitalize() in current_composition:
            print(f"{character.capitalize()} already here")
        if character == "help":
            return

        if character.capitalize() == "Akali":
            akali()

        else:
            if any(character == champ.lower() for champ in champions.keys()):
                if character.lower() not in [i.lower() for i in
                                             current_composition]:
                    current_composition.append(character.capitalize())
                    print(f"{character.capitalize()} has been added\n")
            else:
                print("Enter a valid character\n")


@timer
def group():
    current_traits.clear()
    capped_traits.clear()
    breakpoint_traits.clear()
    remaining_traits.clear()
    first_prior.clear()
    second_prior.clear()
    third_prior.clear()
    no_prior.clear()

    print("*" * 50, "\n")
    if not current_composition:
        return

    print(f"Your composition: {current_composition}")

    for character in current_composition:
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

    print("Your traits:")

    for capped_trait in capped_traits:
        print(capped_trait)

    for breakpoint_trait in breakpoint_traits:
        print(breakpoint_trait)

    sorted_remaining_traits = sorted(
        remaining_traits,
        key=lambda x: traits[x.split(":")[0]][0] - int(
            x.split(":")[1].split()[0]),
    )
    for sorted_remaining_trait in sorted_remaining_traits:
        print(sorted_remaining_trait)
    tailor()


@timer
def tailor():
    print(f"\n\nFirst prio: {first_prior}")
    print(f"Second prio: {second_prior} ")
    print(f"Third prio: {third_prior}")
    print(f"No prio: {no_prior}\n\n")
    suggestions = {name: 0 for name in champions.keys()}

    for trait in first_prior + second_prior + third_prior + no_prior:
        for name, traits in champions.items():
            if name not in current_composition:
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

    for score, characters in scoreboard.items():
        print(f"{score} points: {[', '.join(characters)]}")
    flag_next = False
    while flag_next is not True:
        choice = input("\n\nYour choice: ")
        if choice.capitalize() == "Akali":
            akali()

        if choice not in current_composition:
            if choice.capitalize() in champions.keys():
                current_composition.append(choice.capitalize())
                flag_next = True
                group()


def akali():
    if "Akali" not in current_composition:
        akali_spec = None
        while akali_spec not in ("1", "2"):
            akali_spec = input("\nAkali spec: \n1. K/DA\n2. True Damage\n")

        if akali_spec == "1":
            champions["Akali"].append("K/DA")
            print("K/DA Akali has been added\n")
            current_composition.append("Akali")
        if akali_spec == "2":
            champions["Akali"].append("True Damage")
            print("True Damage Akali has been added\n")
            current_composition.append("Akali")


if __name__ == "__main__":
    data_fill()

    print("\n")
    print("*" * 50, "\n")
    request()
    group()
