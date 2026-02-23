using DelimitedFiles
using HDF5


"""
    do_nci(workspace, country, objectives, maxpts, minpts; kwargs...)

kwargs are:
    * `suffix`
    * `objectives_to_minimize`
    * `minimization_frontier_objectives`

"""
function do_nci(workspace, country, objectives, maxpts, minpts, results_folder;
                suffix="", objectives_to_minimize=[], kwargs...)
    table_folder = joinpath(workspace, country, "ValueTables")
    file_list = [
        "extensification_bmps_irrigated.csv",
        "extensification_bmps_rainfed.csv",
        "extensification_current_practices.csv",
        "extensification_intensified_irrigated.csv",
        "extensification_intensified_rainfed.csv",
        "fixedarea_bmps_irrigated.csv",
        "fixedarea_bmps_rainfed.csv",
        "fixedarea_intensified_irrigated.csv",
        "fixedarea_intensified_rainfed.csv",
        "forestry_expansion.csv",
        "grazing_expansion.csv",
        "restoration.csv",
        "sustainable_current.csv"
    ];
    
    value_columns = [
        "net_econ_value",
        "biodiversity",
        "net_ghg_co2e",
        "carbon",
        "cropland_value",
        "forestry_value",
        "grazing_value",
        "grazing_methane",
        "production_value",
        "transition_cost",
        # "nitrate_cancer_cases",
        # "ground_noxn",
        "noxn_in_drinking_water"
        # "surface_noxn"
    ];

    data = NaturalCapitalIndex.load_objective_tables(
        table_folder, file_list, value_columns
    );

    output_folder = joinpath(workspace, country, results_folder * suffix)
    mkpath(output_folder)
    
    # set up solutions.h5
    sol_file = joinpath(output_folder, "solutions.h5")
    h5open(sol_file, "w") do file
        create_group(file, "solutions")
    end

    # Run the maximization optimization
    scores, sols = NaturalCapitalIndex.random_sample_frontier(
        data, objectives, maxpts, include_endpoints=true, reportvars=value_columns,
        minimize=objectives_to_minimize);
    open(joinpath(output_folder, "summary_table_maximize.csv"), "w") do io
        sid = range(1, stop=size(scores)[1]);
        writedlm(io, [vcat(["ID"], value_columns)], ",");
        writedlm(io, [sid scores], ",");
    end
    h5open(sol_file, "r+") do file
        g = file["solutions"]
        g["maximization", chunk=(1, size(sols)[2]), deflate=6] = sols
    end

    # Run the minimization optimization
    if :minimization_frontier_objectives in keys(kwargs)
        minimization_objectives = kwargs[:minimization_frontier_objectives]
    else
        minimization_objectives = objectives
    end

    scores, sols = NaturalCapitalIndex.random_sample_frontier(
        data, minimization_objectives, minpts, sense=:minimize, reportvars=value_columns,
        minimize=objectives_to_minimize);
    open(joinpath(output_folder, "summary_table_minimize.csv"), "w") do io
        sid = range(1, stop=size(scores)[1]);
        writedlm(io, [vcat(["ID"], value_columns)], ",");
        writedlm(io, [sid scores], ",");
    end
    h5open(sol_file, "r+") do file
        g = file["solutions"]
        g["minimization", chunk=(1, size(sols)[2]), deflate=6] = sols
    end

end
