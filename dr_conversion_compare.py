#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import subprocess
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

plt.rcParams['font.family'] = "Arial"
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['font.size'] = 13
plt.rcParams['figure.dpi'] = 300

def plot(drive_conversion_ngrnas_old, drive_conversion_ngrnas_new):
    """
    Function to plot the drive conversion efficiency for both old and new models.
    Args:
        drive_conversion_ngrnas_old: A list of drive conversion efficiencies for the old model.
        drive_conversion_ngrnas_new: A list of drive conversion efficiencies for the new model.
    """
    gRNAs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    plt.subplots(figsize=(5, 5))

    # Plot old model
    plt.plot(gRNAs, drive_conversion_ngrnas_old, marker='o', linestyle='-', color='b', label='Old Model', clip_on=False, zorder=3)

    # Plot new model
    plt.plot(gRNAs, drive_conversion_ngrnas_new, marker='o', linestyle='-', color='r', label='New Model', clip_on=False, zorder=3)

    plt.xlabel('# gRNAs', fontweight='bold')
    plt.ylabel('Drive Conversion Efficiency', fontweight='bold')

    # Hide the right and top axes
    ax = plt.gca()  # Get the current axis object
    ax.spines['right'].set_visible(False)  # Hide the right axis
    ax.spines['top'].set_visible(False)  # Hide the top axis
    ax.tick_params(axis='both', which='both', length=8, width=1, direction='inout', grid_color='black', grid_alpha=0.5)
    for spine in ax.spines.values():
        spine.set_zorder(0)

    # Set x-axis and y-axis tick parameters
    plt.xlim(1, 12)
    plt.ylim(0.5, 1.01)
    plt.xticks(range(1, 13),)
    plt.yticks()

    # Add legend
    plt.legend(framealpha=0)

    plt.tight_layout()
    plt.show()

def calculate_average(nums):
    total = sum(nums)
    count = len(nums)
    if count > 0:
        average = total / count
        return average
    else:
        return 0

def parse_slim(slim_string):
    """
    Parse the output of SLiM to extract drive conversion efficiency.
    Args:
        slim_string: the entire output of a run of SLiM.
    Return:
        output: the drive conversion rate.
    """
    lines = slim_string.split('\n')
    for line in lines:
        if line.startswith("PYTHON:: "):
            spaced_line = line.split()
            dr_rate = spaced_line[7]  # Extract drive conversion rate from SLiM output

    return dr_rate

def run_slim(command_line_args):
    """
    Runs SLiM using subprocess.
    Args:
        command_line_args: list; a list of command line arguments.
    Return:
        The entire SLiM output as a string.
    """
    slim = subprocess.Popen(command_line_args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
    out, err = slim.communicate()
    #print(err)
    return out

def configure_slim_command_line(args_dict):
    """
    Sets up a list of command line arguments for running SLiM.
    Args:
        args_dict: a dictionary of SLiM parameters.
    Return:
        clargs: A formatted list of the arguments.
    """
    clargs = "slim "
    source = args_dict["source"]
    for arg in args_dict:
        if arg == "source":
            continue
        if isinstance(args_dict[arg], bool):
            clargs += f"-d {arg}={'T' if args_dict[arg] else 'F'} "
        else:
            clargs += f"-d {arg}={args_dict[arg]} "

    clargs += source
    return clargs.split()

def collect_data(args_dict):
    """
    Collect drive conversion efficiency data for a range of gRNAs.
    Args:
        args_dict: A dictionary of SLiM parameters.
    Return:
        drive_conversion_ngrnas: A list of average drive conversion efficiencies for each gRNA count.
    """
    drive_conversion_ngrnas = []
    for num_grnas in range(1, 13):  # The number of gRNAs varies from 1 to 12
        drive_conversions = []
        args_dict['NUM_GRNAS'] = num_grnas
        total_runs =20
        print(f"Running simulations for {num_grnas} gRNAs...")  # Print progress
        for i in range(total_runs):  # Run SLiM 10 times for each NUM_GRNAS value
            print(f"Run {i+1}/{total_runs} for {num_grnas} gRNAs")  # Print current run
            clargs = configure_slim_command_line(args_dict)
            slim_outcome = run_slim(clargs)
            parsed_result = parse_slim(slim_outcome)
            slim_result = float(parsed_result)
            drive_conversion = (slim_result - 0.5) / 0.5  # Calculate drive conversion efficiency
            drive_conversions.append(drive_conversion)
        drive_conversion_ngrnas.append(calculate_average(drive_conversions))

    return drive_conversion_ngrnas

def main():
    # Get args from arg parser:
    parser = ArgumentParser()
    parser.add_argument('-src', '--source', default="one_gen_full_modified.slim", type=str,
                        help=r"SLiM file to be run. Default 'one_gen_full_modified.slim'")
    args_dict = vars(parser.parse_args())

    # Common parameters for both models
    args_dict['CAPACITY'] = 50000000
    args_dict['DROP_SIZE'] = 1000

    # Old Model (original settings)
    args_dict_old = args_dict.copy()
    args_dict_old['DRIVE_FITNESS_VALUE'] = 0.9
    args_dict_old['FEMALE_SOMATIC_FITNESS_VALUE'] = 1.0
    args_dict_old['GENE_DISRUPTION_DRIVE_FITNESS_MULTIPLIER'] = 0.95
    args_dict_old['R1_OCCURRENCE_RATE'] = 0.01
    args_dict_old['HOMING_EDGE_EFFECT'] = 0.055
    args_dict_old['DOUBLE_MISMATCH_PENALTY'] = 1.0

    drive_conversion_ngrnas_old = collect_data(args_dict_old)

    # New Model (modified settings)
    args_dict_new = args_dict.copy()
    args_dict_new['DRIVE_FITNESS_VALUE'] = 1.0
    args_dict_new['FEMALE_SOMATIC_FITNESS_VALUE'] = 1.0
    args_dict_new['GENE_DISRUPTION_DRIVE_FITNESS_MULTIPLIER'] = 1.0
    args_dict_new['R1_OCCURRENCE_RATE'] = 0.01
    args_dict_new['HOMING_EDGE_EFFECT'] = 0.083
    args_dict_new['DOUBLE_MISMATCH_PENALTY'] = 0.313

    drive_conversion_ngrnas_new = collect_data(args_dict_new)

    # Plot comparison
    plot(drive_conversion_ngrnas_old, drive_conversion_ngrnas_new)

if __name__ == "__main__":
    main()