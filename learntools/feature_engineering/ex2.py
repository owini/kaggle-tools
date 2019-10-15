import category_encoders as ce
import pandas as pd

from learntools.core import *

clicks = pd.read_parquet('../input/feature-engineering-data/baseline_data.pqt')

def get_data_splits(valid_fraction=0.1):
    """ Splits a dataframe into train, validation, and test sets. First, orders by 
        the column 'click_time'. Set the size of the validation and test sets with
        the valid_fraction keyword argument.
    """

    dataframe = clicks.sort_values('click_time')
    valid_rows = int(len(dataframe) * valid_fraction)
    train = dataframe[:-valid_rows * 2]
    # valid size == test size, last two sections of the data
    valid = dataframe[-valid_rows * 2:-valid_rows]
    test = dataframe[-valid_rows:]
    
    return train, valid, test


class LeakageQuestion(ThoughtExperiment):
    _solution = ("You should calculate the encodings from the training set only. "
                 "If you include data from the validation and test sets into the encodings, you'll "                
                 "overestimate the model's performance. You should in general be "
                 "vigilant to avoid leakage, that is, including any information from the "
                 "validation and test sets into the model. For a review on this topic, see our "
                 "lesson on [data leakage](https://www.kaggle.com/alexisbcook/data-leakage)"
                )


def count_encodings_solution():
    cat_features = ['ip', 'app', 'device', 'os', 'channel']
    count_enc = ce.CountEncoder(cols=cat_features)

    train, valid, _ = get_data_splits()

    # Learn encoding from the training set
    count_enc.fit(train[cat_features])

    # Apply encoding to the train and validation sets
    train_encoded = train.join(count_enc.transform(train[cat_features]).add_suffix('_count'))
    valid_encoded = valid.join(count_enc.transform(valid[cat_features]).add_suffix('_count'))

    return train_encoded, valid_encoded


class CountEncodings(EqualityCheckProblem):
    _vars = ['train_encoded', 'valid_encoded']
    _hint = ("CountEncoder works like scikit-learn classes with a `.fit` method to calculate "
    "counts and a `.transform` method to apply the encoding. You can join two dataframes with the same "
    "index using `.join` and add suffixes to columns names with `.add_suffix`")
    _solution = CS("""
    # Create the count encoder
    count_enc = CountEncoder(cols=cat_features)

    # Learn encoding from the training set
    count_enc.fit(train[cat_features])

    # Apply encoding to the train and validation sets
    train_encoded = train.join(count_enc.transform(train[cat_features]).add_suffix('_count'))
    valid_encoded = valid.join(count_enc.transform(valid[cat_features]).add_suffix('_count'))
    """)
    _expected = count_encodings_solution()

class CountEncodingEffectiveness(ThoughtExperiment):

    _solution = """
    Rare values tend to have similar counts (with values like 1 or 2), so you can classify rare 
    values together at prediction time. Common values with large counts are unlikely to have 
    the same exact count as other values. So, the common/important values get their own 
    grouping.
    """

def target_encodings_solution():
    cat_features = ['ip', 'app', 'device', 'os', 'channel']
    target_enc = ce.TargetEncoder(cols=cat_features)

    train, valid, _ = get_data_splits()

    # Learn encoding from the training set
    target_enc.fit(train[cat_features], train['is_attributed'])

    # Apply encoding to the train and validation sets
    train_encoded = train.join(target_enc.transform(train[cat_features]).add_suffix('_target'))
    valid_encoded = valid.join(target_enc.transform(valid[cat_features]).add_suffix('_target'))

    return train_encoded, valid_encoded

class TargetEncodings(EqualityCheckProblem):
    _vars = ['train_encoded', 'valid_encoded']
    _hint = ("TargetEncoder works like scikit-learn classes with a `.fit` method to learn the "
    "encoding and a `.transform` method to apply the encoding. Also note that you'll need to tell it "
    "which columns are categorical variables.")
    _solution = CS("""
    # Have to tell it which features are categorical when they aren't strings
    target_enc = ce.TargetEncoder(cols=cat_features)

    # Learn encoding from the training set
    target_enc.fit(train[cat_features], train['is_attributed'])

    # Apply encoding to the train and validation sets
    train_encoded = train.join(target_enc.transform(train[cat_features]).add_suffix('_target'))
    valid_encoded = valid.join(target_enc.transform(valid[cat_features]).add_suffix('_target'))
    """)
    _expected = target_encodings_solution()


class RemoveIPEncoding(ThoughtExperiment):
    _solution = """
    Target encoding attempts to measure the population mean of the target for each 
    level in a categorical feature. This means when there is less data per level, the 
    estimated mean will be further away from the "true" mean, there will be more variance. 
    There is little data per IP address so it's likely that the estimates are much noisier
    than for the other features. The model will rely heavily on this feature since it is 
    extremely predictive. This causes it to make fewer splits on other features, and those
    features are fit on just the errors left over accounting for IP address. So, the 
    model will perform very poorly when seeing new IP addresses that weren't in the 
    training data (which is likely most new data). Going forward, we'll leave out the IP feature when trying
    different encodings.
    """

def cb_encodings_solution():
    cat_features = ['app', 'device', 'os', 'channel']
    cb_enc = ce.CatBoostEncoder(cols=cat_features, random_state=7)

    train, valid, _ = get_data_splits()

    # Learn encoding from the training set
    cb_enc.fit(train[cat_features], train["is_attributed"])

    # Apply encoding to the train and validation sets
    train_encoded = train.join(cb_enc.transform(train[cat_features]).add_suffix('_cb'))
    valid_encoded = valid.join(cb_enc.transform(valid[cat_features]).add_suffix('_cb'))

    return train_encoded, valid_encoded

class CatBoostEncodings(EqualityCheckProblem):
    _vars = ['train_encoded', 'valid_encoded']
    _hint = ("CatBoostEncoder works like scikit-learn classes with a `.fit` method to learn the "
    "encoding and a `.transform` method to apply the encoding. Also note that you'll need to tell it "
    "which columns are categorical variables.")
    _solution = CS("""
    # Have to tell it which features are categorical when they aren't strings
    cb_enc = ce.CatBoostEncoder(cols=cat_features, random_state=7)

    # Learn encoding from the training set
    cb_enc.fit(train[cat_features], train['is_attributed'])

    # Apply encoding to the train and validation sets
    train_encoded = train.join(cb_enc.transform(train[cat_features]).add_suffix('_cb'))
    valid_encoded = valid.join(cb_enc.transform(valid[cat_features]).add_suffix('_cb'))
    """) 
    _expected = cb_encodings_solution()
        

qvars = bind_exercises(globals(), [
    LeakageQuestion,
    CountEncodings,
    CountEncodingEffectiveness,
    TargetEncodings,
    RemoveIPEncoding,
    CatBoostEncodings,
    ],
    tutorial_id=271,
    var_format='q_{n}',
    )
__all__ = list(qvars)
