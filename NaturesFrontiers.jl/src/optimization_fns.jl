using LinearAlgebra
using Random


function random_weights(n)
    w = Random.rand(n)
    return w/sum(w)
end

"""
    make_weight_vectors(npts, ndims)

Generate random weights from a multivariate normal distribution. 

These points are uniformly distributed on the positive octant of a sphere.
"""
function make_weight_vectors(npts, ndims)
    pts = [Random.randn(ndims) for _ in range(1, length=npts)];
    return [abs.(v/norm(v)) for v in pts];
end


function optimize_with_weights(data, objectives, weights)
    mv, idx = findmax(
        sum(w*data[ob] for (w, ob) in zip(weights, objectives)), 
        dims=2);

    return idx
end


function normalize_data(data, objectives)
    normdata = Dict{String, Array{Float64,2}}();
    for ob in objectives
        t = sum(maximum(data[ob], dims=2)); #? Why did I take the sum here?
        normdata[ob] = data[ob] / t;
    end
    return normdata
end

"Returns an `Array` of size `(1, size(objectives))` containing total scores given management choices in `sol`"
function scores_for_sol(data, objectives, sol)
    s = zeros(size(objectives))
    for (i, ob) in enumerate(objectives)
        s[i] = sum(data[ob][sol])
    end
    return s
end


"""
    random_sample_frontier(data, objectives, npts; sense=:maximize, include_endpoints=false, kargs...)

Calculate `scores` and `solutions` for points on the frontier optimizing `objectives` for the given `data`.

Optional `kwargs` are:
    `reportvars`: Expects an array of strings. If this is provided, the output `scores` matrix will 
    include summary values from `data` for the given variables. Otherwise the output will match `objectives`.
    `minimize`: Expects an array of integers indicating which of the `objectives` should be minimized.

"""
function random_sample_frontier(data, objectives, npts; sense=:maximize, include_endpoints=false, kwargs...)
    nobj = length(objectives)
    nparcels = size(data[objectives[1]])[1]
    normdata = normalize_data(data, objectives)
    weights = make_weight_vectors(npts, nobj)
    
    if (include_endpoints)
        for i = 1:length(objectives)
            weights[i][:] .= 0.0
            weights[i][i] = 1.0
        end
    end

    if (sense == :minimize)
        weights = -1 * weights
    end
    
    if :minimize in keys(kwargs)
        for obj in kwargs[:minimize]
            for wv in weights
                wv[obj] *= -1.0
            end
        end
    end

    if :reportvars in keys(kwargs)
        reportvars = kwargs[:reportvars]
    else
        reportvars = objectives
    end


    scores = zeros(npts, length(reportvars))
    solutions = zeros(npts, nparcels)

    Threads.@threads for i = 1:npts
        sol = optimize_with_weights(normdata, objectives, weights[i])
        solutions[i,:] = [c[2] for c in sol]
        scores[i,:] = scores_for_sol(data, reportvars, sol)
    end

    return scores, solutions

end



"""
    get_baseline_scores(data, objectives, baseline_index)
Returns an Array{T, 1} with scores for each objective under the baseline scenario,
identified by `baseline_index`. 
"""
function get_baseline_scores(data, objectives, baseline_index)
    return [sum(data[ob][:,baseline_index]) for ob in objectives]
end