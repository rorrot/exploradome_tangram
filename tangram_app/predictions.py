from .processing import *
from .distances import *
from .moments import *

def img_to_sorted_dists(img_cv, side, prepro):
    cnts, cropped_img = prepro(img_cv, side=side)
    image, contours = merge_tangram(cropped_img, cnts)

    centers, perimeters = distance_formes(cnts)
    distances = ratio_distance(centers, perimeters)
    sorted_dists = sorted_distances(distances)
    
    # get distances
    data = pd.read_csv("data/data.csv", sep=";")
    mses = np.array(mse_distances(data, sorted_dists))

    # get proba
    if np.all((mses == 0)):
        return None

    # fix the issue where some proba == 0
    mses[mses==0] = 0.0001
    proba = np.round(1/mses/np.sum(1/mses), 3)

    # get probabilities
    probas_labelled = data[["classe"]].rename(columns={"classe": "target"})
    probas_labelled.loc[:, "proba"] = proba

    probas_labelled = probas_labelled.sort_values(by=["proba"], ascending=False).reset_index(drop=True)

    # returns sorted probas
    return probas_labelled

def get_predictions(image, prepro, side, hu_moments_dataset="data/hu_moments.csv"):
    """
    compare moments of a frame with the hu moments of our dataset images  

    =========

    Parameters : 

    image : OpenCV image
    hu_moments : dataset with the humoments of each class
    target : name of the classes
    side : which side should be analyzed - left / right / full image

    ========

    Return : print the probabilities to belong to each class in descending order (Pandas DataFrame)

    author : @Nohossat
    """

    # get dataset
    hu_moments = pd.read_csv(hu_moments_dataset)
    target = hu_moments.iloc[:, -1]

    # Our operations on the frame come here
    cnts, img = prepro(image, side=side)
    
    HuMo = find_moments(cnts)

    if len(HuMo) == 0 : 
        return None # the image can't be processed, so empty predictions

    # with the hu_moments we can get the predictions
    HuMo = np.hstack(HuMo)

    # get distances
    dist = hu_moments.apply(lambda row : dist_humoment4(HuMo, row.values[:-1]), axis=1)
    dist_labelled = pd.concat([dist, target], axis=1)
    dist_labelled.columns = ['distance', 'target']

    # get probabilities
    dist_labelled['proba'] = round((1/dist_labelled['distance']) / np.sum( 1/dist_labelled['distance'], axis=0),2)
    probas = dist_labelled.sort_values(by=["proba"], ascending=False)[['target','proba']].reset_index(drop=True)
    
    # sorted probabilities
    return probas

