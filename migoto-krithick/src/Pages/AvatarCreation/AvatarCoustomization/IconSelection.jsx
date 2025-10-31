import React from 'react'
import Gender from '../../../Icons/Gender'
import Shirt from '../../../Icons/Shirt'
import Pant from '../../../Icons/Pant'
import Hair from '../../../Icons/Hair'
import Glass from '../../../Icons/Glass'
import BeardIcon from '../../../Icons/BeardIcon'
import Shoe from '../../../Icons/Shoe'
import styles from '../AvatarCoustomization/AvtCustomiser.module.css'

function IconSelection({setFilter, filter, isBeard, groupedModelConfigs, setModelConfigs, ogConfig , toggleModel}) {
  return (
    <>
    {/* -------------iCon selection ------------ */}
          <div className={styles.avtType}>
            <div
              onClick={() => setFilter("Body")}
              className={`${styles.unselectedType} ${
                filter == "Body" ? styles.selectedType : ""
              }`}
            >
              <Gender filter={filter} />
            </div>
            <div
              onClick={() => setFilter("Shirt")}
              className={`${styles.unselectedType} ${
                filter == "Shirt" ? styles.selectedType : ""
              }`}
            >
              <Shirt filter={filter} />
            </div>
            <div
              onClick={() => setFilter("Pant")}
              className={`${styles.unselectedType} ${
                filter == "Pant" ? styles.selectedType : ""
              }`}
            >
              <Pant filter={filter} />
            </div>
            <div
              onClick={() => setFilter("Hair")}
              className={`${styles.unselectedType} ${
                filter == "Hair" ? styles.selectedType : ""
              }`}
            >
              <Hair filter={filter} />
            </div>
            <div
              onClick={() => setFilter("Glass")}
              className={`${styles.unselectedType} ${
                filter == "Glass" ? styles.selectedType : ""
              }`}
            >
              <Glass filter={filter} />
            </div>
            {isBeard && (
              <div
                onClick={() => setFilter("Beard")}
                className={`${styles.unselectedType} ${
                  filter == "Beard" ? styles.selectedType : ""
                }`}
              >
                {" "}
                <BeardIcon filter={filter} />
              </div>
            )}
            {/* <div
              onClick={() => setFilter("Watch")}
              className={`${styles.unselectedType} ${
                filter == "Watch" ? styles.selectedType : ""
              }`}
            >
              <Watch filter={filter} />
            </div> */}
            <div
              onClick={() => setFilter("Shoes")}
              className={`${styles.unselectedType} ${
                filter == "Shoes" ? styles.selectedType : ""
              }`}
            >
              <Shoe filter={filter} />
            </div>
          </div>
    
    {/* ---------------data selection --------------- */}

    <div className={styles.avtTypeLists}>
        <div className={styles.TypeListsHeading}>
          {`${filter == "Body" ? "Character" : filter}`}
          {filter == "Body" &&
            groupedModelConfigs.map((item) => (
              <div
                className={styles.bar}
                onClick={() => {
                  setModelConfigs(item?.models);
                }}
              >
                {item.name}
              </div>
            ))}
        </div>

        {filter != "Body" && (
          <div
            className={`${styles.TypeListsContainer} 
            ${filter == "Body" ? styles.charModelList : ""}
            `}
          >
            {ogConfig
              ?.filter((model) => model.type === filter)
              .map((model) => (
                <div
                  key={model.id}
                  className={`${styles.modelButtons}  ${
                    filter == "Body" ? styles.charModelButtons : ""
                  }`}
                  onClick={() => toggleModel(model.id)}
                >
                  <img src={model.thumbnail} alt={`${model.type}`} />
                </div>
              ))}
          </div>
        )}
      </div>

    </>
  )
}

export default IconSelection