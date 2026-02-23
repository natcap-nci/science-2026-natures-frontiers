using Pkg
Pkg.activate(".")

using YAML
using DelimitedFiles
using NaturalCapitalIndex

if length(ARGS) > 0
    config_file = ARGS[1]
else
    error("Must provide config file argument")
end

args = YAML.load_file(config_file)
# workspace = Base.Filesystem.joinpath(args["workspace"])
workspace = args["workspace"]
country_file = args["country_list"]

if Base.Filesystem.isfile(country_file)
    country_list = readdlm(country_file, ',', header=false);
else
    country_list = split(strip(country_file), ",")
end

# Set objectives from args or to default
if "optimization_output_folder" in keys(args)
    results_folder = args["optimization_output_folder"]
else
    results_folder = "OptimizationResults"
end
if "objectives" in keys(args)
    objectives = args["objectives"]
else
    objectives = ["net_econ_value", "biodiversity", "net_ghg_co2e"]
end
if "objectives_to_minimize" in keys(args)
    objectives_to_minimize = args["objectives_to_minimize"]
else
    objectives_to_minimize = []
end
if "minimization_objectives" in keys(args)
    minimization_frontier_objectives = args["minimization_objectives"]
else
    minimization_frontier_objectives = objectives
end

# run optimizations
for country in country_list
    println(country)
    do_nci(workspace, country, objectives, 5000, 10, results_folder,
        objectives_to_minimize=objectives_to_minimize,
        minimization_frontier_objectives=minimization_frontier_objectives,
        suffix="");

    # try
    #     do_nci(workspace, country, objectives, 5000, 10, results_folder,
    #         objectives_to_minimize=objectives_to_minimize,
    #         minimization_frontier_objectives=minimization_frontier_objectives,
    #         suffix="");
    # catch e
    #     open("runtime_error.log", "a") do file
    #         println(file, country)
    #     end
    # end

end





# objectives = ["net_econ_value", "biodiversity", "carbon", "nitrate_cancer_cases"];
# minimization_frontier_objectives = ["ag_value", "biodiversity", "carbon", "nitrate_cancer_cases"];

# for country in country_list
#     println(country)
#     try
#         do_nci(workspace, country, objectives, 5000, 1000,
#             objectives_to_minimize=[4],
#             minimization_frontier_objectives=minimization_frontier_objectives,
#             suffix="");
#     catch e
#         open("runtime_error.log", "a") do file
#             println(file, country)
#         end
#     end
# end


