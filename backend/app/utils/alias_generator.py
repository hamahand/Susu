import hashlib
from typing import List


# List of 100 Adinkra symbol names with their meanings
ADINKRA_NAMES = [
    "GyeNyame", "Sankofa", "Adinkrahene", "Dwennimmen", "Funtumfunefu Denkyemfunefu",
    "Akoma", "Duafe", "Nsoromma", "Mate Masie", "Aya", "Fawohodie", "Nkyinkyim",
    "Bese Saka", "Akokonan", "Eban", "Nyame Dua", "Akofena", "Mpatapo", "Wawa Aba",
    "Nyansapo", "Asase Ye Duru", "Bi Nka Bi", "Odo Nnyew Fie Kwan", "Kintinkantan",
    "Sepow", "Kwatakye Atiko", "Epa", "Akoma Ntoso", "Nkonsonskonso", "Osram Ne Nsoromma",
    "Denkyem", "Hye Won Hye", "Mframadan", "Owuo Atwedee", "Dame-Dame", "Kramo Bone Amma Yeanhu Kramo Pa",
    "Mmere Dane", "Fihankra", "Okodee Mmowere", "Boa Me Na Me MMOA Wo", "Owo Foro Adobe",
    "Nsaa", "Aban", "Akoben", "Ani Bere A Enso Gya", "Fofoo", "Asaawa", "Dono Ntoaso",
    "Gye W'ani", "Hwemudua", "Kete Pa", "Me Ware Wo", "Mmra Krado", "Mmrafo Ani Ase",
    "Mmrafu Krado", "Mpuannum", "Musuyidee", "Nea Onnim No Sua A Ohu", "Nea Ope Se Obedi Hene",
    "Nkyimu", "Nyame Nnwu Na Mawu", "Nyame Nti", "Nyame Ye Ohene", "Onyankopon Adom Nti Biribiara Beye Yie",
    "Pempamsie", "Sesa Wo Suban", "Tamfo Bebre", "Woforo Dua Pa A", "Wo Nsa Da Mu A",
    "Ese Ne Tekrema", "Abodee", "Adwo", "Agyindawuru", "Abe Dua", "Ahoden", "Akoma Kurukuruwa",
    "Akoma Yemu", "Ananse Ntontan", "Apatam", "Asante Sika", "Boafo Yena", "Damas",
    "Denkyem Mmowere", "Dwenini Dua", "Fafanto", "Gyawu Atiko", "Hwehwemu Dua", "Kaide",
    "Kokuroko", "Kokuromotie", "Kontire Ne Akwamu", "Kye Kye Kuule", "Mako", "Menso Wo Kenten",
    "Mmogo", "Nea Onnim No Sua A Ohu", "Nyame Biribi Wo Soro", "Okuafo Pa", "Sunsum", "UAC Nkanea"
]


def generate_member_alias(user_id: int, group_id: int) -> str:
    """
    Generate a deterministic alias for a user in a specific group.
    
    Args:
        user_id: The user's ID
        group_id: The group's ID
        
    Returns:
        A deterministic alias like "GyeNyame-A7B3"
    """
    # Create a hash from user_id and group_id for consistency
    hash_input = f"{user_id}_{group_id}".encode('utf-8')
    hash_value = hashlib.md5(hash_input).hexdigest()
    
    # Use first 8 characters of hash for the suffix
    suffix = hash_value[:8].upper()
    
    # Select Adinkra name based on hash
    name_index = int(hash_value[:2], 16) % len(ADINKRA_NAMES)
    adinkra_name = ADINKRA_NAMES[name_index]
    
    return f"{adinkra_name}-{suffix}"
