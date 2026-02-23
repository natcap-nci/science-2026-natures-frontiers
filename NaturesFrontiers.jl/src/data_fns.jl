using CSV
using DataFrames
using DelimitedFiles


function read_country_list_file(list_file)
    return readdlm(list_file, ',', String)
end


function load_objective_tables(data_folder, scenario_files, objective_columns)
    data = load_data(data_folder; file_list=scenario_files);
    values = Dict{String, Array{Float64,2}}();
    for ob in objective_columns
        values[ob] = NaturalCapitalIndex.extract_matrix(data, ob);
    end
    return values;
end


"""
    load_data(data_dir; file_list=nothing, col_list=nothing)
Loads the csv files in `data_dir`.
"""
function load_data(data_dir; file_list=nothing,
                   col_list=nothing)
    if file_list === nothing
        files = Base.Filesystem.readdir(data_dir)
        file_list = [f for f in files if
                     Base.Filesystem.splitext(f)[2]==".csv"]
    end

    data = Dict{String, DataFrame}()

    for f in file_list
        name = Base.Filesystem.splitext(f)[1]
        full_path = Base.Filesystem.joinpath(data_dir, f)
        data[name] = DataFrame(CSV.File(full_path))
        if col_list !== nothing
            if typeof(col_list) != Vector{Symbol}
                col_list = [Symbol(c) for c in col_list]
            end
            data[name] = data[name][:,col_list]
        end
    end

    return data
end


function extract_matrix(df_dict, column; key_order=nothing)
    if key_order === nothing
        key_order = sort(collect(keys(df_dict)))
    end
    # c = convert(Symbol, column)

    result = zeros((length(df_dict[key_order[1]][!, column]),
                    length(key_order)))

    for (i, k) in enumerate(key_order)
        result[:, i] = convert(Vector{Float64}, df_dict[k][!, column])
    end

    return result
end


function extract_vector(df_dict, column)
    k = first(keys(df_dict))
    # c = convert(Symbol, column)
    v = convert(Vector{Float64}, df_dict[k][!, column])
    return v
end
