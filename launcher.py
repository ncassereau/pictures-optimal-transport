import subprocess
import uuid
import os
import conf


def make_command(file, command, **kwargs):
    file.write("#!/bin/bash\n\n")

    # Use slurm parameters put in the configuration file
    for arg, value in kwargs.items():
        arg = arg.replace("_", "-")
        file.write(f"#SBATCH --{arg}={value}\n")

    # Do not overwrite stdout and stderr of previous step
    file.write("#SBATCH --open-mode=append\n")

    file.write("#SBATCH --exclusive\n\n")

    file.write("set -e\n")

    # Get in the working directory
    file.write("cd ${SLURM_SUBMIT_DIR}\n")

    # Load the correct module
    file.write(f"module purge\nmodule load {conf.module_to_load}\n")

    # Display the (start) date
    file.write('echo "JOB $SLURM_JOBID START TIME: $(date)"\n')

    # Execute our command
    if isinstance(command, (list, tuple)):
        command = " ".join(command)
    file.write("srun python3 " + command + "\n")

    # Display the (end) date
    file.write('echo "JOB $SLURM_JOBID END TIME: $(date)"\n')
    file.write('echo "-------------------"\n')
    file.write('echo "-------------------" 1>&2;\n')


def sbatch(file_path):
    out = subprocess.run(["sbatch", file_path], capture_output=True)

    if out.returncode != 0: # Submission failed for some reason
        # Decode and remove trailing \n since print already inserts a newline
        print(out.stderr.decode("utf-8")[:-1])
        exit(out.returncode)

    # As explained above, decode and remove trailing \n
    output = out.stdout.decode('utf-8')[:-1]
    print(output)
    jobid = int(output.split(" ")[-1])
    return jobid


def run(command, dependency_id=None, **kwargs):
    filename = str(uuid.uuid1()) + ".slurmfile"

    with open(filename, "w") as file:

        if dependency_id is not None: # Add a dependency if not the first step
            kwargs["dependency"] = f"afterok:{dependency_id}"

        # Make submission file
        make_command(file, command, **kwargs)

    # Submit job and delete submission file
    jobid = sbatch(filename)
    os.remove(filename)

    return jobid


def execute(command1=None, command2=None, command3=None):
    if command1 is not None:
        jobid1 = run(
            command1,
            **conf.slurm_kwargs,
            nodes=1,
            ntasks_per_node=1,
            cpus_per_task=conf.ntasks
        )
    else:
        jobid1 = None # for the dependency of command2
    
    if command2 is not None:
        jobid2 = run(
            command2,
            dependency_id=jobid1,
            **conf.slurm_kwargs,
            nodes=conf.scatter_nodes,
            ntasks_per_node=conf.ntasks // conf.scatter_cpus_per_task,
            cpus_per_task=conf.scatter_cpus_per_task
        )
    else:
        jobid2 = None # for the dependency of command3

    if command3 is not None:
        _ = run(
            command3,
            dependency_id=jobid2,
            **conf.slurm_kwargs,
            nodes=1,
            ntasks_per_node=1,
            cpus_per_task=conf.ntasks
        )


def main():
    if conf.use_slurm: # flush slurm stdout and stderr
        subprocess.run([f"> {conf.slurm_kwargs['output']}"], shell=True)
        subprocess.run([f"> {conf.slurm_kwargs['error']}"], shell=True)
    command1 = "transport.py"
    command2 = "make_pics.py"
    command3 = "merge_pics.py"
    execute(command1, command2, command3)


if __name__ == "__main__":
    main()
