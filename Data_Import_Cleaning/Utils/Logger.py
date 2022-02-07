class Logger:
    def __init__(self, logfile):
        """Initializes a minimal logger by creating a logfile.

        Parameters:
             logfile (str): Absolute Path to the logfile.
        """
        self.logfile = logfile
        with open(self.logfile, 'w') as logfile:
            logfile.write("Logfile generated. ")


    def __call__(self, entry):
        self.log(entry)


    def log(self, entry):
        """Writes a specific entry to the logfile.

        Parameters:
            entry (str): Entry to be written

        Returns:
            None
        """
        with open(self.logfile, 'a') as logfile:
            logfile.write("{}\n".format(entry))
