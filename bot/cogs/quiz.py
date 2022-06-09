""" Shopkeeper Quiz """
import asyncio
import random
import time

import discord
from discord.commands import slash_command
from discord.ext import commands

NEUTRAL_ITEMS = ["Keen Optic", "Royal Jelly", "Poor Mans Shield", "Ocean Heart", "Iron Talon", "Mango Tree", "Arcane Ring", "Elixir", "Broom Handle", "Ironwood Tree", "Trusty Shovel", "Faded Broach", "Grove Bow", "Vampire Fangs", "Ring Of Aquila", "Repair Kit", "Pupils Gift", "Helm Of The Undying", "Imp Claw", "Philosophers Stone", "Dragon Scale", "Essence Ring", "Nether Shawl", "Craggy Coat", "Greater Faerie Fire", "Quickening Charm", "Mind Breaker", "Third Eye", "Spider Legs", "Vambrace",
                 "Clumsy Net", "Enchanted Quiver", "Paladin Sword", "Orb Of Destruction", "Titan Sliver", "Witless Shako", "Timeless Relic", "Spell Prism", "Princes Knife", "Flicker", "Telescope", "Ninja Gear", "Illusionists Cape", "Havoc Hammer", "Magic Lamp", "The Leveller", "Minotaur Horn", "Force Boots", "Seer Stone", "Mirror Shield", "Fallen Sky", "Fusion Rune", "Apex", "Ballista", "Woodland Striders", "Trident", "Book Of The Dead", "Pirate Hat", "Ex Machina", "Desolator 2", "Phoenix Ash"]
ITEMS = ["Abyssal Blade", "Aegis of the Immortal", "Aeon Disk", "Aether Lens", "Aghanims Scepter", "Animal Courier", "Arcane Boots", "Armlet of Mordiggian", "Assault Cuirass", "Band of Elvenskin", "Battle Fury", "Belt of Strength", "Black King Bar", "Blade Mail", "Blade of Alacrity", "Blades of Attack", "Blight Stone", "Blink Dagger", "Bloodstone", "Bloodthorn", "Boots of Speed", "Boots of Travel", "Bottle", "Bracer", "Broadsword", "Buckler", "Butterfly", "Chainmail", "Cheese", "Circlet", "Clarity", "Claymore", "Cloak", "Crimson Guard", "Crown", "Crystalys", "Daedalus", "Dagon", "Demon Edge", "Desolator", "Diffusal Blade", "Divine Rapier", "Dragon Lance", "Drum of Endurance", "Dust of Appearance", "Eaglesong", "Echo Sabre", "Enchanted Mango", "Energy Booster", "Ethereal Blade", "Euls Scepter of Divinity", "Eye of Skadi", "Faerie Fire", "Flying Courier", "Force Staff", "Gauntlets of Strength", "Gem of True Sight", "Ghost Scepter", "Glimmer Cape", "Gloves of Haste", "Guardian Greaves", "Hand of Midas", "Headdress", "Healing Salve", "Heart of Tarrasque", "Heavens Halberd", "Helm of Iron Will", "Helm of the Dominator", "Holy Locket", "Hood of Defiance", "Hurricane Pike", "Hyperstone", "Infused Raindrop", "Iron Branch", "Iron Talon", "Javelin", "Kaya", "Kaya and Sange", "Linkens Sphere",
         "Lotus Orb", "Maelstrom", "Magic Stick", "Magic Wand", "Manta Style", "Mantle of Intelligence", "Mask of Madness", "Medallion of Courage", "Mekansm", "Meteor Hammer", "Mithril Hammer", "Mjollnir", "Monkey King Bar", "Moon Shard", "Morbid Mask", "Mystic Staff", "Necronomicon", "Null Talisman", "Nullifier", "Oblivion Staff", "Observer Ward", "Octarine Core", "Ogre Club", "Orb of Venom", "Orchid Malevolence", "Perseverance", "Phase Boots", "Pipe of Insight", "Platemail", "Point Booster", "Power Treads", "Quarterstaff", "Quelling Blade", "Radiance", "Reaver", "Refresher Orb", "Refresher Shard", "Ring of Aquila", "Ring of Basilius", "Ring of Health", "Ring of Protection", "Ring of Regen", "Ring of Tarrasque", "Robe of the Magi", "Rod of Atos", "Sacred Relic", "Sages Mask", "Sange", "Sange and Yasha", "Satanic", "Scythe of Vyse", "Sentry Ward", "Shadow Amulet", "Shadow Blade", "Shivas Guard", "Silver Edge", "Skull Basher", "Slippers of Agility", "Smoke of Deceit", "Solar Crest", "Soul Booster", "Soul Ring", "Spirit Vessel", "Staff of Wizardry", "Stout Shield", "Tango", "Tome of Knowledge", "Town Portal Scroll", "Tranquil Boots", "Urn of Shadows", "Vanguard", "Veil of Discord", "Vitality Booster", "Vladmirs Offering", "Void Stone", "Wind Lace", "Wraith Band", "Yasha", "Yasha and Kaya"]
HEROES = ["Abaddon", "Alchemist", "Ancient Apparition", "Anti-Mage", "Antimage", "Arc Warden", "Axe", "Bane", "Batrider", "Beastmaster", "Bloodseeker", "Bounty Hunter", "Brewmaster", "Bristleback", "Broodmother", "Centaur Warrunner", "Chaos Knight", "Chen", "Clinkz", "Clockwerk", "Crystal Maiden", "Dark Seer", "Dark Willow", "Dazzle", "Death Prophet", "Disruptor", "Doom", "Dragon Knight", "Drow Ranger", "Earth Spirit", "Earthshaker", "Elder Titan", "Ember Spirit", "Enchantress", "Enigma", "Faceless Void", "Grimstroke", "Gyrocopter", "Huskar", "Invoker", "Io", "Jakiro", "Juggernaut", "Keeper of the Light", "Kunkka", "Legion Commander", "Leshrac", "Lich", "Lifestealer", "Lina", "Lion", "Lone Druid", "Luna", "Lycan", "Magnus", "Mars", "Medusa", "Meepo", "Mirana", "Monkey King", "Morphling", "Naga Siren",
          "Natures Prophet", "Natures Prophet", "Necrophos", "Night Stalker", "Nyx Assassin", "Ogre Magi", "Omniknight", "Oracle", "Outworld Devourer", "Pangolier", "Phantom Assassin", "Phantom Lancer", "Phoenix", "Puck", "Pudge", "Pugna", "Queen of Pain", "Razor", "Riki", "Rubick", "Sand King", "Shadow Demon", "Shadow Fiend", "Shadow Shaman", "Silencer", "Skeleton King", "Skywrath Mage", "Slardar", "Slark", "Snapfire", "Sniper", "Spectre", "Spirit Breaker", "Storm Spirit", "Sven", "Techies", "Templar Assassin", "Terrorblade", "Tidehunter", "Timbersaw", "Tinker", "Tiny", "Treant Protector", "Troll Warlord", "Tusk", "Underlord", "Undying", "Ursa", "Vengeful Spirit", "Venomancer", "Viper", "Visage", "Void Spirit", "Warlock", "Weaver", "Windranger", "Winter Wyvern", "Witch Doctor", "Wraith King", "Zeus"]
OTHER = ["Radiant", "Dire", "Axe Attacks", "DotA", "IceFrog", "Battle Pass", "We Need Wards", "Deny",
         "Last Hit", "Space Created", "Feeder", "Report", "Commend", "The International", "Princess of the Moon"]
KILLS = ["Double Kill", "Triple Kill", "Ultra Kill", "Rampage", "Killing Spree", "Dominating",
         "Mega Kill", "Unstoppable", "Wicked Sick", "Monster Kill", "Godlike", "Beyond Godlike", "Ownage"]
SPELLS = ["Acid Spray", "Adaptive Strike", "Aftershock", "Alacrity", "Anchor Smash", "Ancient Seal", "Aphotic Shield", "Arc Lightning", "Arcane Aura", "Arcane Bolt", "Arcane Curse", "Arcane Orb", "Arcane Supremacy", "Arctic Burn", "Arena of Blood", "Assassinate", "Assimilate", "Astral Imprisonment", "Astral Spirit", "Atrophy Aura", "Attribute Shift", "Avalanche", "Bad Juju", "Ball Lightning", "Bash of the Deep", "Battery Assault", "Battle Cry", "Battle Hunger", "Battle Trance", "Bedlam", "Berserkers Blood", "Berserkers Call", "Berserkers Rage", "Black Hole", "Blade Dance", "Blade Fury", "Blast Off!", "Blinding Light", "Blink", "Blink Strike", "Blood Rite", "Bloodlust", "Bloodrage", "Blur", "Borrowed Time", "Boulder Smash", "Boundless Strike", "Brain Sap", "Bramble Maze", "Breathe Fire", "Bulldoze", "Bulwark", "Burning Army", "Burning Spear", "Burrow", "Burrowstrike", "Call Down", "Call of the Wild Boar", "Call of the Wild Hawk", "Caustic Finale", "Centaur War Stomp", "Chain Frost", "Chakra Magic", "Chakram", "Chaos Bolt", "Chaos Meteor", "Chaos Strike", "Chaotic Offering", "Charge of Darkness", "Chemical Rage", "Chilling Touch", "Chronosphere", "Cinder Brew", "Cloak and Dagger", "Cold Embrace", "Cold Feet", "Cold Snap", "Concussive Shot", "Conjure Image", "Consume", "Corrosive Haze", "Corrosive Skin", "Counter Helix", "Counterspell", "Coup de Grace", "Cripple", "Crippling Fear", "Crypt Swarm", "Crystal Nova", "Culling Blade", "Curse of Avernus", "Cursed Crown", "Cyclone", "Dark Ascension", "Dark Pact", "Dark Rift", "Deafening Blast", "Death Pulse", "Death Ward", "Decay", "Decrepify", "Degen Aura", "Demonic Conversion", "Demonic Purge", "Desolate", "Devour", "Diabolic Edict", "Dismember", "Dispel Magic", "Dispersion", "Disruption", "Divided We Stand", "Divine Favor", "Doppelganger", "Double Edge", "Dragon Blood", "Dragon Slave", "Dragon Tail", "Dream Coil", "Drunken Brawler", "Dual Breath", "Duel", "Earth Spike", "Earth Splitter", "Earthbind", "Earthshock", "Echo Slam", "Echo Stomp", "Eclipse", "Eject", "Elder Dragon Form", "Electric Vortex", "EMP", "Empower", "Enchant", "Enchant Remnant", "Enchant Totem", "Enfeeble", "Enrage", "Ensnare", "Entangling Claws", "Epicenter", "Equilibrium", "Essence Shift", "Ether Shock", "Ethereal Jaunt", "Exorcism", "Exort", "Eye of the Storm", "Eyes in the Forest", "Fade Bolt", "False Promise", "Fatal Bonds", "Fates Edict", "Feast", "Feral Impulse", "Fervor", "Fiends Grip", "Fiery Soul", "Finger of Death", "Fire Remnant", "Fire Spirits", "Fireblast", "Firefly", "Firestorm", "Fissure", "Flak Cannon", "Flame Guard", "Flamebreak", "Flaming Fists", "Flaming Lasso", "Flesh Golem", "Flesh Heap", "Flux", "Focus Fire", "Focused Detonate", "Forge Spirit", "Fortify Tower", "Fortunes End", "Freezing Field", "Frost Arrows", "Frost Blast", "Frost Shield", "Frostbite", "Fury Swipes", "Geminate Attack", "Geomagnetic Grip", "Ghost Shroud", "Ghost Walk", "Ghostship", "Glaives of Wisdom", "Glimpse", "Global Silence", "Gods Rebuke", "Gods Strength", "Grave Chill", "Gravekeepers Cloak", "Greater Bash", "Greevils Greed", "Grow", "Guardian Angel", "Guardian Sprint", "Gush", "Gust", "Hand of God", "Haunt", "Headshot", "Healing Ward", "Heartstopper Aura", "Heat Seeking Missile", "Heavenly Grace", "Hex", "Holy Persuasion", "Homing Missile", "Hoof Stomp", "Hookshot", "Howl", "Hunter in the Night", "Icarus Dive", "Ice Blast", "Ice Path", "Ice Shards", "Ice Vortex", "Ice Wall", "Ignite", "Illuminate", "Illusory Orb", "Impale", "Impetus", "Incapacitating Bite", "Infernal Blade", "Infest", "Ink Swell", "Inner Beast", "Inner Fire", "Insatiable Hunger", "Invisibility", "Invoke", "Ion Shell", "Jinada", "Jingu Mastery", "Juxtapose", "Kinetic Field", "Kraken Shell", "Laguna Blade", "Laser", "Last Word", "Launch Fire Spirit", "Launch Snowball", "Leap", "Leech Seed", "Life Break", "Life Drain", "Light Strike Array", "Lightning Bolt", "Lightning Storm", "Liquid Fire", "Living Armor",
          "Lucent Beam", "Lucky Shot", "Lunar Blessing", "Macropyre", "Magic Missile", "Magnetic Field", "Magnetize", "Maledict", "Malefice", "Mana Break", "Mana Burn", "Mana Drain", "Mana Leak", "Mana Shield", "Mana Void", "March of the Machines", "Marksmanship", "Mass Serpent Ward", "Meat Hook", "Meld", "Metamorphosis", "Midnight Pulse", "Minefield Sign", "Mirror Image", "Mischief", "Mist Coil", "Moment of Courage", "Moon Glaives", "Moonlight Shadow", "Morph", "Morph Replicate", "Mortal Strike", "Multicast", "Multishot", "Mystic Flare", "Mystic Snake", "Natural Order", "Natures Attendants", "Natures Call", "Natures Grasp", "Necromastery", "Nether Blast", "Nether Strike", "Nether Swap", "Nether Ward", "Nethertoxin", "Nightmare", "Nightmare End", "Nimbus", "Omnislash", "Open Wounds", "Overcharge", "Overgrowth", "Overload", "Overpower", "Overwhelming Odds", "Paralyzing Cask", "Penitence", "Permanent Immolation", "Phantasm", "Phantom Rush", "Phantom Strike", "Phantoms Embrace", "Phase Shift", "Pit of Malice", "Plague Ward", "Plasma Field", "Poison Attack", "Poison Nova", "Poison Sting", "Poison Touch", "Poof", "Pounce", "Power Cogs", "Powershot", "Presence of the Dark Lord", "Press the Attack", "Primal Roar", "Primal Split", "Primal Spring", "Proximity Mines", "Psi Blades", "Psionic Trap", "Pulse Nova", "Pulverize", "Purification", "Purifying Flames", "Quas", "Quill Spray", "Rage", "Ransack", "Ravage", "Reactive Armor", "Reality", "Reality Rift", "Reapers Scythe", "Rearm", "Recall", "Reflection", "Refraction", "Regeneration", "Reincarnation", "Release", "Relocate", "Remote Mines", "Requiem of Souls", "Retaliate", "Return", "Reverse Polarity", "Revert Form", "Rip Tide", "Rocket Barrage", "Rocket Flare", "Rolling Boulder", "Rolling Thunder", "Rot", "Rupture", "Sacred Arrow", "Sand Storm", "Sanitys Eclipse", "Savage Roar", "Scorched Earth", "Scream of Pain", "Searing Arrows", "Searing Chains", "Shackles", "Shackleshot", "Shadow Dance", "Shadow Poison", "Shadow Realm", "Shadow Strike", "Shadow Walk", "Shadow Wave", "Shadow Word", "Shadowraze", "Shallow Grave", "Shapeshift", "Shield Crash", "Shockwave", "Shrapnel", "Shukuchi", "Shuriken Toss", "Silence", "Sinister Gaze", "Skeleton Walk", "Skewer", "Sleight of Fist", "Slithereen Crush", "Smoke Screen", "Snowball", "Song of the Siren", "Sonic Wave", "Soul Assumption", "Soul Catcher", "Soul Rip", "Soulbind", "Spark Wraith", "Spawn Spiderite", "Spawn Spiderlings", "Spear of Mars", "Spectral Dagger", "Spell Steal", "Spiderling Poison Sting", "Spiked Carapace", "Spin Web", "Spirit Lance", "Spirit Link", "Spirit Siphon", "Spirits", "Splinter Blast", "Split Earth", "Split Shot", "Sprout", "Stampede", "Starstorm", "Stasis Trap", "Static Field", "Static Link", "Static Remnant", "Static Storm", "Sticky Napalm", "Stifling Dagger", "Stone Form", "Stone Gaze", "Stone Remnant", "Storm Hammer", "Stroke of Fate", "Sun Ray", "Sun Strike", "Sunder", "Supernova", "Surge", "Swashbuckle", "Tag Team", "Take Aim", "Telekinesis", "Telekinesis Land", "Teleportation", "Tempest Double", "Terrorize", "Tether", "The Swarm", "Thirst", "Throw Unstable Concoction", "Thunder Clap", "Thunder Strike", "Thundergods Wrath", "Tidebringer", "Timber Chain", "Time Dilation", "Time Lapse", "Time Lock", "Time Walk", "Toggle Movement", "Tombstone", "Tornado", "Torrent", "Toss", "Track", "Trap", "Tree Dance", "Tree Grab", "Tree Throw", "Tricks of the Trade", "True Form", "Unburrow", "Unrefined Fireblast", "Unstable Concoction", "Untouchable", "Upheaval", "Vacuum", "Vampiric Aura", "Vendetta", "Vengeance Aura", "Venomous Gale", "Viper Strike", "Viscous Nasal Goo", "Void", "Voodoo Restoration", "Wall of Replica", "Walrus Kick", "Walrus Punch", "Waning Rift", "Warcry", "Warpath", "Wave of Terror", "Waveform", "Wex", "Whirling Axes", "Whirling Death", "Wild Axes", "Will-o-Wisp", "Wind Walk", "Windrun", "Winters Curse", "Wraithfire Blast", "Wrath of Nature", "Wukongs Command", "X Marks the Spot"]
NEW_SPELLS = ["Death Pact", "Essence Flux", "Multishot",
              "Natures Grasp", "Storm Surge", "Wolf Bite"]
ALL_WORDS = NEUTRAL_ITEMS + ITEMS + HEROES + OTHER + KILLS + SPELLS + NEW_SPELLS


def scramble(word):
    """ Scrambles a string """
    char_list = list(word)
    random.shuffle(char_list)
    return ''.join(char_list)


def scramble_easy(word):
    """ Scrambles a string, leaving spaces in place """
    scrambled = ""
    for w in word.split(" "):
        scrambled += scramble(w) + " "
    return scrambled[:-1]  # remove trailing space


def get_next_word(blacklist):
    """ Gets the next word, category, and index """
    n = random.randint(0, len(ALL_WORDS)-1)
    # Avoid words we have used before
    while n in blacklist:
        n = random.randint(0, len(ALL_WORDS)-1)

    # quick maths - this is faster than using "if word in NEUTRAL_ITEMS"
    if n >= len(ALL_WORDS) - len(NEW_SPELLS) - len(SPELLS):
        category = "Spells"
    elif n >= len(NEUTRAL_ITEMS) + len(ITEMS) + len(HEROES):
        category = "Phrases"
    elif n >= len(NEUTRAL_ITEMS) + len(ITEMS):
        category = "Heroes"
    elif n >= len(NEUTRAL_ITEMS):
        category = "Items"
    else:
        category = "Neutral Items"

    word = ALL_WORDS[n]

    return word, category, n


class ShopkeeperQuiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quiz_in_progress = {}  # key = guild.id, value = Bool
        self.database = self.bot.get_cog('Database')

    def in_progress(self, guild):
        """ Returns True if a quiz is currently in progress """
        return self.quiz_in_progress.get(guild.id, False)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignore own reactions
        if user == self.bot.user:
            return

        # Ignore messages not sent by the bot
        if reaction.message.author != self.bot.user:
            return

        # NEW quiz
        if reaction.emoji in "🆕":
            """ Remove own reaction and start quiz """
            try:
                await reaction.remove(self.bot.user)
            except discord.errors.NotFound:
                pass
            asyncio.ensure_future(
                self.shopkeeper_quiz(
                    bot=self.bot,
                    channel=reaction.message.channel,
                    guild=reaction.message.guild
                ))
        else:
            # Unknown emoji, do nothing
            return

        # Remove the reaction once the job is done
        try:
            await reaction.remove(user)
        except discord.errors.NotFound:
            pass

    async def shopkeeper_quiz(self, bot, channel, guild, game_state=None, respond=False):
        # Initialize Game State
        if game_state is None:
            # scores contains users' scores (key is user.id)
            # correct_answers contains users' number of correct answers (key is user.id)
            # words contains the index of words we have seen before to avoid duplicates in the same quiz
            game_state = dict(round=1, scores={}, correct_answers={}, words=[])

        # Don't start a new quiz if there's already a quiz happening
        if game_state['round'] == 1 and self.in_progress(guild):
            if respond:
                await channel.respond("A quiz is in progress!")
            else:
                await channel.send("A quiz is in progress!")
            return

        # Begin the quiz
        self.quiz_in_progress[guild.id] = True
        answer, category, n = get_next_word(game_state['words'])
        game_state['words'].append(n)
        max_gold = 25  # total possible gold for this answer

        # Each round has three phases that last 30 seconds each
        round_time = 30
        # If all 3 phases end without a correct answer, the game is over

        # Called for each response, returns True if the guess is correct
        def check(msg):
            guess = msg.content.lower().replace("'", "").strip()
            return guess == answer.lower()

        # Phase 1: hard scramble
        embed = discord.Embed()
        embed.title = f"Shopkeeper's Quiz (round {game_state['round']})"
        embed.description = f"**Unscramble:** {scramble(answer).upper()}"
        if respond:
            quiz_message = await channel.respond(embed=embed)
            quiz_message = await quiz_message.original_message()
        else:
            quiz_message = await channel.send(embed=embed)
        start_time = time.perf_counter()

        try:
            # Wait another 30 seconds after sending the message
            correct_msg = await bot.wait_for('message', check=check, timeout=int(round_time))

        except asyncio.TimeoutError:
            # Phase 2: another hard scramble + category hint
            embed.description = f"**Unscramble:** {scramble(answer).upper()}\n**Category:** {category} "
            embed.set_footer(text="Here's a hint!")
            await quiz_message.edit(embed=embed)

            try:
                # Wait another 30 seconds after hint was given
                correct_msg = await bot.wait_for('message', check=check, timeout=int(round_time))
            except asyncio.TimeoutError:
                # Phase 3: easy scramble + category hint
                embed.description = f"**Unscramble:** {scramble_easy(answer).upper()}\n**Category:** {category}"
                embed.set_footer(text="Here's another hint!")
                await quiz_message.edit(embed=embed)
                try:
                    # Wait another 30 seconds after the last hint is given
                    correct_msg = await bot.wait_for('message', check=check, timeout=int(round_time))
                except asyncio.TimeoutError:
                    # Timed out, nobody answered - stop the quiz
                    await quiz_message.add_reaction("👎")
                    embed.description += "\n**Answer**: {}".format(answer)
                    embed.set_footer(
                        text="Nobody answered in time! Game over.")
                    try:
                        await quiz_message.edit(embed=embed)
                    except discord.errors.NotFound:
                        pass

                    # Find the winner(s)
                    try:
                        top_score = max(game_state['scores'].values())
                    except ValueError:
                        top_score = 0
                    winners = [self.bot.get_user(
                        k) for k, v in game_state['scores'].items() if v == top_score]
                    if len(winners) == 0:
                        text = "Everybody lost!"
                    elif len(winners) == 1:
                        correct = game_state['correct_answers'][winners[0].id]
                        text = "Winner: **{}** earned **{}** gold with {} answers!\n".format(
                            winners[0].display_name, top_score, correct)
                    else:
                        text = "It's a tie! The following players earned **{}** gold:\n".format(
                            (top_score))
                        for winner in winners:
                            text += " -- {}\n".format(winner)

                    # Find the loser(s)
                    losers = [self.bot.get_user(
                        k) for k, v in game_state['scores'].items() if v != top_score]
                    if len(losers) > 0:
                        text += "Losers:\n"
                        for user in losers:
                            correct = game_state['correct_answers'][user.id]
                            gold = game_state['scores'][user.id]
                            text += " -- {} got {} correct (**{}** gold)\n".format(
                                user.display_name, correct, gold)

                    winner_embed = discord.Embed()
                    winner_embed.description = text
                    winner_embed.title = "Shopkeeper's Quiz Results"
                    winner_embed.set_thumbnail(
                        url="https://i.imgur.com/Xyf1VjQ.png")
                    winner_embed.set_footer(
                        text=f"To play again, press NEW or type /quiz")
                    winner_message = await channel.send(embed=winner_embed)
                    await winner_message.add_reaction("🆕")

                    # Increment user's gold amounts
                    for user in winners + losers:
                        gold = game_state['scores'][user.id]
                        self.database.user_add_gold(user, gold)

                    game_state['round'] = 1
                    game_state['scores'] = dict()
                    self.quiz_in_progress[guild.id] = False
                    return

        # Increment user's score in the game state
        elasped_time = time.perf_counter() - start_time
        score = int(max_gold - (elasped_time * max_gold / (round_time * 3)))
        user = correct_msg.author
        try:
            game_state['scores'][user.id] += score
            game_state['correct_answers'][user.id] += 1
        except KeyError:
            game_state['scores'][user.id] = score
            game_state['correct_answers'][user.id] = 1

        await correct_msg.add_reaction("👍")
        embed.description += f"\n**Answer**: {answer}"
        embed.set_footer(
            text=f"Answered by {user.display_name} for {score} gold.")
        await quiz_message.edit(embed=embed)

        # Continue the quiz!
        game_state['round'] += 1
        asyncio.ensure_future(self.shopkeeper_quiz(
            channel=channel, bot=bot, guild=guild, game_state=game_state))

    @slash_command(name="quiz", description="Play the Shopkeeper's quiz")
    async def quiz(self, ctx):
        await self.shopkeeper_quiz(channel=ctx, bot=ctx.bot, guild=ctx.guild, respond=True)


def setup(bot):
    print("Loading Shopkeeper Quiz cog")
    bot.add_cog(ShopkeeperQuiz(bot))
    print("Loaded Shopkeeper Quiz cog")
