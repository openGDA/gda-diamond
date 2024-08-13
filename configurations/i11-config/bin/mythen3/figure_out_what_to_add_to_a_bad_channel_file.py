def get_module_and_channel(some_number):
    module = int(some_number / 1280)
    channel = some_number % 1280
    print(f"You should add {channel} to /dls_sw/i11/software/mythen3/diamond/calibration/bad_d{module}.chans")
