import sys
import matplotlib.pyplot as plt
import helics as h
import logging
import numpy as np

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def destroy_federate(fed):
    grantedtime = h.helicsFederateRequestTime(fed, h.HELICS_TIME_MAXTIME)
    status = h.helicsFederateDisconnect(fed)
    h.helicsFederateFree(fed)
    h.helicsCloseLibrary()
    logger.info("Federate Finalized")


def calc_charging_voltage(EV_list):
    charging_voltage = []
    charge_voltages = [120, 240, 630]
    for EV in EV_list:
        if EV == 1:
            charging_voltage.append(charge_voltages[0])
        elif EV == 2:
            charging_voltage.append(charge_voltages[1])
        elif EV == 3:
            charging_voltage.append(charge_voltages[2])
        else:
            charging_voltage.append(0)

    return charging_voltage


def get_new_EV(numEVs):
    lvl1 = 0.05
    lvl2 = 0.6
    lvl3 = 0.35
    listOfEVs = np.random.choice([1, 2, 3], numEVs, p=[lvl1, lvl2, lvl3]).tolist()
    numLvl1 = listOfEVs.count(1)
    numLvl2 = listOfEVs.count(2)
    numLvl3 = listOfEVS.count(3)

    return numLvl1, numLvl2, numLvl3, listOfEVs


def main(argv):
    np.random.seed(628)

    fed = h.helicsCreateValueFederateFromConfig("ChargerConfig.json")
    federate_name = h.helicsFederateGetName(fed)
    logger.info(f"Created federate {federate_name}")

    sub_count = h.helicsFederateGetInputCount(fed)
    logger.debug(f"\tNumber of subscriptions: {sub_count}")
    pub_count = h.helicsFederateGetPublicationCount(fed)
    logger.debug(f"\tNumber of publications: {pub_count}")

    subid = {}
    for i in range(0, sub_count):
        subid[i] = h.helicsFederateGetInputByIndex(fed, i)
        sub_name = h.helicsInputGetTarget(subid[i])
        logger.debug(f"\tRegistered subscription---> {sub_name}")

    pubid = {}
    for i in range(0, pub_count):
        pubid[i] = h.helicsFederateGetPublicationByIndex(fed, i)
        pub_name = h.helicsPublicationGetName(pubid[i])
        logger.debug(f"\tRegistered publication---> {pub_name}")

    h.helicsFederateEnterExecutingMode(fed)
    logger.info("Entered HELICS execution mode")

    simulated_hours = 24 * 7
    total_interval = int(
        60 * 60 * simulated_hours
    )  # total_interval here represented in seconds
    update_interval = int(
        h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_PERIOD)
    )
    grantedtime = 0

    ### COSIMULATION BLOCK
    while grantedtime < total_interval:
        # Time request for the next physical interval to be simulated
        requested_time = grantedtime + update_interval
        logger.debug(f"Requesting time {requested_time}")
        grantedtime = h.helicsFederateRequestTime(fed, requested_time)
        logger.debug(f"Granted time {grantedtime}")

    destroy_federate(fed)


if __name__ == "__main__":
    main(sys.argv)
