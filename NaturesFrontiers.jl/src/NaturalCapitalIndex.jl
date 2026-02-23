module NaturalCapitalIndex
include("data_fns.jl")
include("optimization_fns.jl")
include("main_fns.jl")

export load_objective_tables, load_data, make_weight_vectors, optimize_with_weights,
    normalize_data, scores_for_sol, random_sample_frontier, read_country_list_file,
    get_baseline_scores, do_nci

end # module
