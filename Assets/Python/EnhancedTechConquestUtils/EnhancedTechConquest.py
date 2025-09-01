from CvPythonExtensions import *
import CvUtil

# Removed global references to reduce memory overhead

# Configuration cache to avoid repeated parsing
_config_cache = None


def loadConfigurationData():
    """Load configuration with memory optimization and caching"""
    global _config_cache

    # Return cached config if already loaded
    if _config_cache is not None:
        return _config_cache

    # Use local variables to reduce memory footprint
    import SystemPaths
    path = SystemPaths.modDir + "\\Assets\\Caveman2Cosmos Config.ini"

    import ConfigParser
    Config = ConfigParser.ConfigParser()
    Config.read(path)

    # Initialize with defaults to avoid repeated checks
    config_dict = {
        'check_prereq': True,
        'base_offset': 0,
        'pop_percent': 15,
        'tech_behind_percent': 300,
        'final_modifier': 100
    }

    if Config:
        # Process configuration more efficiently
        try:
            # Check Prereq
            val = Config.get("Enhanced Tech Conquest", "Check Prereq")
            config_dict['check_prereq'] = val not in ("False", "false", "0")

            # Base Percent Offset
            val = Config.get("Enhanced Tech Conquest", "Base Percent Offset")
            if val.isdigit():
                config_dict['base_offset'] = int(val)

            # Population Percent
            val = Config.get("Enhanced Tech Conquest", "Population Percent")
            if val.isdigit():
                config_dict['pop_percent'] = int(val)

            # Techs Behind Percent
            val = Config.get("Enhanced Tech Conquest", "Techs Behind Percent")
            if val.isdigit():
                config_dict['tech_behind_percent'] = int(val)

            # Final Modifier
            val = Config.get("Enhanced Tech Conquest", "Final Modifier")
            if val.isdigit():
                config_dict['final_modifier'] = int(val)
        except:
            pass  # Use defaults on any error

    # Build output string more efficiently using list join
    output_parts = [
        "Enhanced Tech Conquest:",
        "\tTechnology Transfer Ignore Prereq = %s" % str(config_dict['check_prereq']),
        "\tBase Technology Transfer Percent. = %d" % config_dict['base_offset'],
        "\tPercentage Per City Population... = %d" % config_dict['pop_percent'],
        "\tPercentage Per Tech Behind... = %d" % config_dict['tech_behind_percent'],
        "\tFinal Modifier... = %d" % config_dict['final_modifier']
    ]
    print
    "\n".join(output_parts)

    # Cache the configuration
    _config_cache = config_dict
    return config_dict


class EnhancedTechConquest:
    """Enhanced Tech Conquest with memory optimizations"""

    # Use __slots__ to reduce memory overhead for instances
    __slots__ = ()

    def onCityAcquired(self, argsList):
        """Handle city acquisition with optimized memory usage"""
        # Early exit if not conquest
        if not argsList[3]:
            return

        # Load configuration (cached after first call)
        config = loadConfigurationData()

        # Early exit check
        base_percent = config['base_offset']
        if base_percent < 1 and config['tech_behind_percent'] < 1:
            return

        # Get game context objects only when needed
        gc = CyGlobalContext()

        iOwnerNew = argsList[1]
        player_new = gc.getPlayer(iOwnerNew)

        # Early exit for NPC
        if player_new.isNPC():
            return

        # Cache frequently used values
        pop_percent = config['pop_percent']
        if pop_percent < 0:
            pop_percent = 0

        # Get player and team objects
        player_old = gc.getPlayer(argsList[0])
        team_old = gc.getTeam(player_old.getTeam())
        team_new = gc.getTeam(player_new.getTeam())

        # Pre-calculate values once
        check_prereq = config['check_prereq']
        tech_behind_percent = config['tech_behind_percent']
        final_modifier = config['final_modifier']

        # Use more memory-efficient data structure
        # Instead of two lists, use a single list with tuples including priority
        tech_list = []
        techs_behind = 0

        # Get the total number of techs once
        num_techs = gc.getNumTechInfos()

        # Single pass through techs
        for iTech in xrange(num_techs):
            # Skip if conditions not met
            if (team_new.isHasTech(iTech) or
                    not team_old.isHasTech(iTech) or
                    not player_new.canResearch(iTech, False, False)):
                continue

            techs_behind += 1

            # Check if can research immediately
            immediate = player_new.canResearch(iTech, True, True)

            if check_prereq and not immediate:
                continue

            # Calculate values once
            cost = team_new.getResearchCost(iTech)
            remaining = cost - team_new.getResearchProgress(iTech)

            # Store as tuple with priority flag
            if immediate:
                tech_list.append((1, iTech, cost, remaining))
            else:
                # Calculate adjusted remaining once
                if remaining > cost * 2 / 3:
                    adjusted = remaining / 3
                elif remaining > cost / 2:
                    adjusted = remaining / 2
                elif remaining > cost / 3:
                    adjusted = remaining * 2 / 3
                else:
                    adjusted = remaining - 1
                tech_list.append((0, iTech, cost, adjusted))

        # Early exit if no techs
        if not tech_list:
            return

        # Calculate base percent with techs behind
        base_percent += techs_behind * tech_behind_percent / 100.0
        if base_percent < 1:
            return

        # Get city and calculate population factor if needed
        city = argsList[2]

        if pop_percent:
            population = city.getPopulation() + 1
            total_pop = player_old.getTotalPopulation() + population
            is_capital = city.isCapital()
            # Calculate force factor more efficiently
            force = pop_percent * (1 + is_capital) * population / (100.0 * total_pop)
        else:
            force = 0

        # Check if human player for messages
        is_human = player_new.isHuman()

        # Pre-calculate values for efficiency
        num_techs = len(tech_list)

        if num_techs > 1:
            base_div = num_techs / 4.0
            attenuation = 100.0 / base_div

        # Process techs
        count = 0
        got_tech = False
        message_parts = []  # More efficient than string concatenation

        # Get game object for random
        game = gc.getGame()

        # Get commerce char once if needed
        if is_human:
            beaker_char = gc.getCommerceInfo(CommerceTypes.COMMERCE_RESEARCH).getChar()

        # Process techs in random order
        while tech_list:
            # Get random index
            idx = game.getSorenRandNum(len(tech_list), "random")

            # Extract tech data and remove from list
            priority, iTech, cost, remaining = tech_list.pop(idx)

            # Update remaining if needed
            if not priority and got_tech and player_new.canResearch(iTech, True, True):
                remaining = cost - team_new.getResearchProgress(iTech)
            elif not priority:
                cost = remaining

            # Calculate percent
            if pop_percent:
                percent = base_percent + base_percent * force
                if percent <= 0:
                    continue
            else:
                percent = base_percent
                if percent <= 0:
                    # Clean up before returning
                    del tech_list
                    return

            # Calculate beakers
            if num_techs > 1:
                beakers_float = cost * percent / (20 * (num_techs - 1) + attenuation * (count + base_div))
            else:
                beakers_float = cost * percent / 100

            # Apply final modifier
            if final_modifier > 0:
                beakers_float = beakers_float * (100 + final_modifier) / 100
            elif final_modifier < 0:
                beakers_float = beakers_float * 100 / (100 - final_modifier)

            beakers = int(beakers_float)

            if beakers < 1:
                continue

            if beakers > remaining:
                beakers = remaining
                if priority == 1:
                    got_tech = True

            # Apply research progress
            team_new.changeResearchProgress(iTech, beakers, iOwnerNew)

            # Build message if human
            if is_human:
                tech_desc = gc.getTechInfo(iTech).getDescription()
                message_parts.append("\n\t* %s <-> %i%c" % (tech_desc, beakers, beaker_char))

            count += 1

        # Send message if human
        if is_human:
            translator = CyTranslator()

            if count:
                # Build message efficiently
                base_msg = translator.getText("TXT_KEY_ENHANCED_TECH_CONQUEST_SUCESS", ()) % city.getName()
                full_msg = base_msg + "".join(message_parts)
            else:
                full_msg = translator.getText("TXT_KEY_ENHANCED_TECH_CONQUEST_FAIL", ()) % city.getName()

            # Get color once
            color = ColorTypes(gc.getInfoTypeForString("COLOR_GREEN"))

            # Get button
            button = gc.getCivilizationInfo(player_old.getCivilizationType()).getButton()

            # Send message
            CvUtil.sendMessage(
                full_msg, iOwnerNew, 20,
                button,
                color, city.getX(), city.getY(), True, True
            )

        # Explicit cleanup of local references
        del tech_list
        del message_parts