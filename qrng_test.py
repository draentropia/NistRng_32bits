#
# Copyright (C) 2019 Luca Pasqualini
# University of Siena - Artificial Intelligence Laboratory - SAILab
#
# Inspired by the work of David Johnston (C) 2017: https://github.com/dj-on-github/sp800_22_tests
#
# NistRng is licensed under a BSD 3-Clause.
#
# You should have received a copy of the license along with this
# work. If not, see <https://opensource.org/licenses/BSD-3-Clause>.
#
# Adapted by Elisabeth Ortega (HPCNow!) - September 2023
#
# Import packages
import sys
import numpy

# Import src
from nistrng import *

# Import QRNG libraries
#from QusideQRNGLALUser.quside_QRNG_LAL_user import QusideQRNGLALUser

"""
Function to specify the origin of the input data.
By default, it will take the input from QRNG machine.
"""
def data_collection(mock=False, data_path=""):

    array= []
    # Use extracted datasets from QRNG.
    if mock:
        with open(data_path, 'r') as file:
            for line in file.readlines():
                array.append(int(line.split("\n")[0]))
            
    else:
        """ To initialize the class is need the QRNG IP address. """
        lib = QusideQRNGLALUser(ip='10.120.30.8')

        """ This variable has to be set to 0. """
        devIndex = 0

        # Get extracted random numbers in bytes
        # 1024*3907 for 1M samples
        array = lib.get_random(1024*3907,devIndex)

        """
        This function disconnect the QRNG.
        """
        lib.disconnect()

    return array

# Función para convertir un número en binario y rellenarlo a 32 bits
"""
Function to convert an integer to a 32 bits binary.
"""
def int_to_binary_32bit(num):
    binary = bin(num)[2:] 
    return '0' * (32 - len(binary)) + binary

        
"""
Function to encode the integer string to binary.
Three methods:
- encode_val: encode all 32 bits. 
- map_val: map values to (-128, 128) range (signed int8).
- last_bits: take the last 8 bits of the string (DEFAULT).
"""
def encode_input(array, encode_method="encode_val"):

    binary_sequence = []

    if encode_method=="encode_val":
        binary_sequence = numpy.array([int(char) for char in list(''.join([int_to_binary_32bit(num) for num in array]))])
        return binary_sequence
    
    if encode_method=="map_val":
        factor  = (2**8-1)/2**32-1

        new_array = [(num * factor - 127) for num in array]

    if encode_method=="last_bits":
        new_array = [(num & 255) - 127 for num in array]

    sequence: numpy.ndarray = numpy.array(array, dtype=int)
    binary_sequence: numpy.ndarray = pack_sequence(sequence)

    return binary_sequence


if __name__ == "__main__":

    """
    Leave arguments empty to use QRNG instrument.
    Set "True" and type the path to use a dataset.
    """    
    array = data_collection(True, "/home/eortega/coding/cesga-qrng/small_output.txt")

    """
    @args array  
    @opts - empty: encode 32 bits),
    use "map_val" for mapping or "last_bits" for using
    only the last 8 bits of the string.
    """
    binary_sequence = encode_input(array)

    # Check the eligibility of the test and generate an eligible battery from the default NIST-sp800-22r1a battery
    eligible_battery: dict = check_eligibility_all_battery(binary_sequence, SP800_22R1A_BATTERY)
    # Print the eligible tests
    print("Eligible test from NIST-SP800-22r1a:")
    for name in eligible_battery.keys():
        print("-" + name)
    # Test the sequence on the eligible tests
    results = run_all_battery(binary_sequence, eligible_battery, False)
    # Print results one by one
    print("Test results:")
    for result, elapsed_time in results:
        if result.passed:
            print("- PASSED - score: " + str(numpy.round(result.score, 3)) + " - " + result.name + " - elapsed time: " + str(elapsed_time) + " ms")
        else:
            print("- FAILED - score: " + str(numpy.round(result.score, 3)) + " - " + result.name + " - elapsed time: " + str(elapsed_time) + " ms")
