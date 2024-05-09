import math
import numpy as np


def influx_step(t:np.ndarray, weight:float, conc:float, dose:float, rate:float, t0:float)->np.ndarray:
    """Contrast agent flux (mmol/sec) generated by step injection.

    Args:
        t (numpy.ndarray): time points in sec where the flux is to be calculated.
        weight (float): weight of the subject in kg.
        conc (float): concentration of the contrast agent in mmol/mL.
        dose (float): injected dose in mL/kg body weight.
        rate (float): rate of contrast agent injection in mL/sec.
        t0 (float): start of the injection in sec.
        
    Raises:
        ValueError: if the injection duration is zero, or smaller than the time step of the time array.

    Returns:
        numpy.ndarray: contrast agent flux for each time point in units of mmol/sec.

    Example:

        >>> import numpy as np
        >>> import dcmri as dc

        Create an array of time points covering 20sec in steps of 1.5sec. 

        >>> t = np.arange(0, 20, 1.5)

        Inject a dose of 0.2 mL/kg bodyweight at a rate of 3mL/sec starting at t=5sec. 
        For a subject weighing 70 kg and a contrast agent with concentration 0.5M, this produces the flux:

        >>> dc.influx_step(t, 70, 0.5, 5, 0.2, 3)
        array([0. , 0. , 0. , 0. , 1.5, 1.5, 1.5, 0. , 0. , 0. , 0. , 0. , 0. ,0. ])
    """

    # Get timings
    duration = weight*dose/rate     # sec = kg * (mL/kg) / (mL/sec)
    dt = np.amin(t[1:]-t[:-1])

    # Check consistency of timings
    if dose > 0:
        if duration==0:
            msg = 'Invalid input variables. \n' 
            msg = 'The injection duration is zero.'
            raise ValueError(msg)
        if dt >= duration:
            msg = 'Invalid input variables. \n' 
            msg = 'The smallest time step dt ('+dt+' sec) is larger than the injection duration 1 (' + duration + 'sec). \n'
            msg = 'We would recommend dt to be at least 5 times smaller.'
            raise ValueError(msg)

    # Build flux 
    Jmax = conc*rate                # mmol/sec = (mmol/ml) * (ml/sec)
    J = np.zeros(t.size)
    J[(t0 < t) & (t < t0 + duration)] = Jmax
    return J


def ca_conc(agent:str)->float:
    """Contrast agent concentration

    Args:
        agent (str): Generic contrast agent name, all lower case. Examples are 'gadobutrol', 'gadobenate', etc.

    Raises:
        ValueError: If no data are available for the agent.

    Returns:
        float: concentration in mmol/mL

    Notes:
        Sources: 
            `<https://mriquestions.com/so-many-gd-agents.html>`_
            `<https://www.bayer.com/sites/default/files/2020-11/primovist-pm-en.pdf>`_
            `<https://www.medicines.org.uk/emc/product/2876/smpc#gref>`_

    Example:

        >>> import dcmri as dc
        >>> print('gadobutrol is available in a solution of', dc.ca_conc('gadobutrol'), 'M')
        gadobutrol is available in a solution of 1.0 M
    """    
    if agent == 'gadoxetate':
        return 0.25     # mmol/mL
    if agent == 'gadobutrol':
        return 1.0      # mmol/mL
    if agent in [
            'gadopentetate',
            'gadobenate',
            'gadodiamide',
            'gadoterate',
            'gadoteridol',
            'gadopiclenol',
        ]:
        return 0.5  # mmol/mL 
    raise ValueError('No concentration data for contrast agent ' + agent)


def ca_std_dose(agent:str)->float:
    """Standard injection volume (dose) in mL per kg body weight.

    Args:
        agent (str): Generic contrast agent name, all lower case. Examples are 'gadobutrol', 'gadobenate', etc.

    Raises:
        ValueError: If no data are available for the agent.

    Returns:
        float: Standard injection volume in mL/kg.

    Notes:
        Sources: 
            `<https://mriquestions.com/so-many-gd-agents.html>`_
            `<https://www.bayer.com/sites/default/files/2020-11/primovist-pm-en.pdf>`_
            `<https://www.medicines.org.uk/emc/product/2876/smpc#gref>`_

    Example:

        >>> import dcmri as dc
        >>> print('The standard clinical dose of gadobutrol is', dc.ca_std_dose('gadobutrol'), 'mL/kg')
        The standard clinical dose of gadobutrol is 0.1 mL/kg
    """    
    #"""Standard dose in mL/kg""" # better in mmol/kg, or offer it as an option
    if agent == 'gadoxetate':
        # https://www.bayer.com/sites/default/files/2020-11/primovist-pm-en.pdf
        return 0.1  # mL/kg
    if agent == 'gadobutrol':
        return 0.1      # mL/kg
    if agent == 'gadopiclenol':
        return 0.1      # mL/kg
    if agent in [
            'gadopentetate',
            'gadobenate',
            'gadodiamide',
            'gadoterate',
            'gadoteridol',
            ]:
        return 0.2      # mL/kg
    raise ValueError('No dosage data for contrast agent ' + agent)


def relaxivity(field_strength=3.0, tissue='plasma', agent='gadoxetate', type='T1')->float: 
    """Contrast agent relaxivity values in units of Hz/M

    Args:
        field_strength (float, optional): Field strength in Tesla. Defaults to 3.0.
        tissue (str, optional): Tissue type - options are 'plasma', 'hepatocytes'. Defaults to 'plasma'.
        agent (str, optional): Generic contrast agent name, all lower case. Examples are 'gadobutrol', 'gadobenate', etc.. Defaults to 'gadoxetate'.
        type (str, optional): transverse (T2) or longitudinal (T1) relaxivity. Defaults to 'T1'.

    Returns:
        float: relaxivity in Hz/M or 1/(sec*M)

    Notes:
        Sources: 
            `<https://journals.lww.com/investigativeradiology/FullText/2005/11000/Comparison_of_Magnetic_Properties_of_MRI_Contrast.5.aspx>`_
            Szomolanyi P, et al. Comparison of the Relaxivities of Macrocyclic Gadolinium-Based Contrast Agents in Human Plasma at 1.5, 3, and 7 T, and Blood at 3 T. Invest Radiol. 2019 Sep;54(9):559-564. doi: 10.1097/RLI.0000000000000577.

    Example:

        >>> import dcmri as dc
        >>> print('The plasma relaxivity of gadobutrol at 3T is', 1e-3*dc.relaxivity(3.0, 'plasma', 'gadobutrol'), 'Hz/mM')
        The plasma relaxivity of gadobutrol at 3T is 5.0 Hz/mM    
    """    
    
    rel = {}
    rel['T1'] = {
        'plasma': {
            'gadopentetate':{ #Magnevist
                0.4: 3.8, 
                1.5: 4.1,
                3.0: 3.7,
                4.0: 3.8,
            },
            'gadobutrol': { # Gadovist
                0.4: 6.1, 
                1.5: 5.2,
                3.0: 5.0,
                4.0: 4.7,
            },
            'gadoteridol': { #Prohance
                0.4: 4.8, 
                1.5: 4.1,
                3.0: 3.7,
                4.0: 3.7,
            },
            'gadobenade': { #Multihance
                0.4: 9.2, 
                1.5: 6.3,
                3.0: 5.5,
                4.0: 5.2,
            },
            'gadoterate': { # Dotarem
                0.4: 4.3, 
                1.5: 3.6,
                3.0: 3.5,
                4.0: 3.3,
            },
            'gadodiamide': { #Omniscan
                0.4: 4.4, 
                1.5: 4.3,
                3.0: 4.0,
                4.0: 3.9,
            },
            'mangafodipir': { #Teslascan
                0.4: 3.6, 
                1.5: 3.6,
                3.0: 2.7,
                4.0: 2.2,
            },
            'gadoversetamide': {#Optimark
                0.4: 5.7, 
                1.5: 4.7,
                3.0: 4.5,
                4.0: 4.4,
            },
            'ferucarbotran': { #Resovist
                0.4: 15, 
                1.5: 7.4,
                3.0: 3.3,
                4.0: 1.7,
            },
            'ferumoxide': { #Feridex
                1.5: 4.5,
                3.0: 2.7,
                4.0: 1.2,
            },
            'gadoxetate': { # Primovist
                0.4: 8.7, 
                1.5: 8.1,
                3.0: 6.4,
                4.0: 6.4,
                7.0: 6.2,
                9.0: 6.1
            },
        },
        'hepatocytes': {
            'gadoxetate': {
                1.5: 14.6,
                3.0: 9.8,
                4.0: 7.6,
                7.0: 6.0,
                9.0: 6.1,
            },
        },
    }
    field = math.floor(field_strength)
    try:
        return 1000*rel[type][tissue][agent][field]
    except:
        msg = 'No relaxivity data for ' + agent + ' at ' + str(field_strength) + ' T.'
        raise ValueError(msg)


def T1(field_strength=3.0, tissue='blood', Hct=0.45)->float:
    """T1 value of selected tissue types

    Args:
        field_strength (float, optional): Field strength in Tesla. Defaults to 3.0.
        tissue (str, optional): Tissue type. Defaults to 'blood'.
        Hct (float, optional): Hematocrit value - ignored when tissue is not blood. Defaults to 0.45.

    Raises:
        ValueError: If the requested T1 values are not available.

    Returns:
        float: T1 values in sec

    Example:

        >>> import dcmri as dc
        >>> print('The T1 of liver at 1.5T is', 1e3*dc.T1(1.5, 'liver'), 'msec')
        The T1 of liver at 1.5T is 602.0 msec
    """    
    T1val = {
        'blood':{
            1.0: 1.480,
            3.0: 1/(0.52 * Hct + 0.38),  # Lu MRM 2004
        },
        'liver':{
            1.0: 0.602, # liver R1 in 1/sec (Waterton 2021)
            3.0: 0.752, # liver R1 in 1/sec (Waterton 2021)
            4.0: 1/1.281, # liver R1 in 1/sec (Changed from 1.285 on 06/08/2020)
            7.0: 1/1.109,  # liver R1 in 1/sec (Changed from 0.8350 on 06/08/2020)
            9.0: 1/0.920, # per sec - liver R1 (https://doi.org/10.1007/s10334-021-00928-x)
        },
        'kidney':{
            # Reference values average over cortext and medulla from Cox et al
            # https://academic.oup.com/ndt/article/33/suppl_2/ii41/5078406
            1.0: ((1024+1272)/2) / 1000,
            3.0: ((1399+1685)/2) / 1000,
        },
    }  
    try:
        return T1val[tissue][math.floor(field_strength)]
    except:
        msg = 'No T1 values for ' + tissue + ' at ' + str(field_strength) + ' T.'
        raise ValueError(msg)


def aif_parker(t, BAT:float=0.0)->np.ndarray:
    """Population AIF model as defined by `Parker et al (2006) <https://onlinelibrary.wiley.com/doi/full/10.1002/mrm.21066>`_

    Args:
        t (array_like): time points in units of sec. 
        BAT (float, optional): Time in seconds before the bolus arrives. Defaults to 0 sec (no delay). 

    Returns:
        np.ndarray: Concentrations in M for each time point in t. If t is a scalar, the return value is a scalar too.

    References:
        Adapted from a contribution by the QBI lab of the University of Manchester to the `OSIPI code repository <https://github.com/OSIPI/DCE-DSC-MRI_CodeCollection>`_. 
        
    Example:

        >>> import numpy as np
        >>> import dcmri as dc

        Create an array of time points covering 20sec in steps of 1.5sec, which rougly corresponds to the first pass of the Paeker AIF:

        >>> t = np.arange(0, 20, 1.5)

        Calculate the Parker AIF at these time points, and output the result in units of mM:

        >>> 1000*dc.aif_parker(t)
        array([0.08038467, 0.23977987, 0.63896354, 1.45093969, 
        2.75255937, 4.32881325, 5.6309778 , 6.06793854, 5.45203828,
        4.1540079 , 2.79568217, 1.81335784, 1.29063036, 1.08751679])
    """

    # Check input types
    if not np.isscalar(BAT):
        raise ValueError('BAT must be a scalar')

    # Convert from secs to units used internally (mins)
    t_offset = np.array(t)/60 - BAT/60

    #A1/(SD1*sqrt(2*PI)) * exp(-(t_offset-m1)^2/(2*var1))
    #A1 = 0.833, SD1 = 0.055, m1 = 0.171
    gaussian1 = 5.73258 * np.exp(
        -1.0 *
        (t_offset - 0.17046) * (t_offset - 0.17046) /
        (2.0 * 0.0563 * 0.0563) )
    
    #A2/(SD2*sqrt(2*PI)) * exp(-(t_offset-m2)^2/(2*var2))
    #A2 = 0.336, SD2 = 0.134, m2 = 0.364
    gaussian2 = 0.997356 * np.exp(
        -1.0 *
        (t_offset - 0.365) * (t_offset - 0.365) /
        (2.0 * 0.132 * 0.132))
    # alpha*exp(-beta*t_offset) / (1+exp(-s(t_offset-tau)))
    # alpha = 1.064, beta = 0.166, s = 37.772, tau = 0.482
    sigmoid = 1.050 * np.exp(-0.1685 * t_offset) / (1.0 + np.exp(-38.078 * (t_offset - 0.483)))

    pop_aif = gaussian1 + gaussian2 + sigmoid
    
    return pop_aif/1000 # convert to M