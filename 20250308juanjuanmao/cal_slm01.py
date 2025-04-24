import numpy as np
import pysal as ps
from pysal.model import spreg
import geopandas as gpd
from sklearn.preprocessing import MinMaxScaler
from libpysal.weights import KNN
from spreg import ML_Lag
import os
from datetime import datetime

def run_spatial_regression(gdf):
    """Run spatial regression model and return results dictionary"""
    try:
        # Select features and prepare data
        selected_features = ['ashcan', 'poster', 'green', 'sky', 'window', 
                            'chair', 'OpenSocial', 'shop', 'h_value', 'traffic']
        y = gdf['attraction'].values.reshape(-1, 1)
        
        # Normalize data
        scaler = MinMaxScaler(feature_range=(0, 1))
        X = scaler.fit_transform(gdf[selected_features])
        y = scaler.fit_transform(y).flatten()
        
        # Create weights matrix
        k = min(2, len(gdf)-1)  # Ensure k doesn't exceed number of features
        W = KNN.from_dataframe(gdf, k=k)
        
        # Run spatial regression model
        slm = ML_Lag(y, X, W, name_y='attraction', name_x=selected_features)
        
        return {
            # 'summary': slm.summary,
            'logll': slm.logll,
            'aic': slm.aic,
            'rho': slm.rho
        }
    except Exception as e:
        print(f"Error in spatial regression: {str(e)}")
        return None

def main():
    # Set directories
    input_dir = r"e:\work\sv_juanjuanmao\20250308\八条路线"
    output_file = r"e:\work\sv_juanjuanmao\20250308\八条路线\combined_model_results.txt"
    
    # Get all 04.shp files
    shp_files = [f for f in os.listdir(input_dir) if f.endswith("04.shp")]
    
    if not shp_files:
        print("No 04.shp files found in the directory.")
        return
    
    # Prepare combined results
    combined_results = []
    header = f"Spatial Regression Results - Combined Report\n"
    header += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"Total files processed: {len(shp_files)}\n"
    header += "="*80 + "\n\n"
    combined_results.append(header)
    
    # Process each file
    for filename in shp_files:
        file_path = os.path.join(input_dir, filename)
        try:
            gdf = gpd.read_file(file_path)
            results = run_spatial_regression(gdf)
            
            if results:
                file_header = f"FILE: {filename}\n"
                file_header += "-"*60 + "\n"
                combined_results.append(file_header)
                
                # combined_results.append(results['summary'] + "\n")
                
                stats = (f"Log likelihood: {results['logll']}\n"
                         f"AIC: {results['aic']}\n"
                         f"Spatial coefficient (rho): {results['rho']}\n"
                         "-"*60 + "\n\n")
                combined_results.append(stats)
                
                print(f"Processed: {filename}")
        except Exception as e:
            error_msg = f"Error processing {filename}: {str(e)}\n\n"
            combined_results.append(error_msg)
            print(error_msg)
    
    # Save combined results to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(combined_results)
    
    print(f"\nAll files processed. Results saved to: {output_file}")

if __name__ == "__main__":
    main()