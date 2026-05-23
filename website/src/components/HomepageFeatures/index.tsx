import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: ReactNode;
  link?: {to: string; label: string};
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Distributed by default',
    description: (
      <>
        Built on Dask. Hashtag, mention, and n-gram histograms fan out across
        your cluster and return as pandas DataFrames.
      </>
    ),
    link: {to: '/docs/concepts/architecture', label: 'Architecture →'},
  },
  {
    title: 'Python or R, your choice',
    description: (
      <>
        Every analytic ships in two flavors. <code>*_alt_python</code> wraps{' '}
        <code>advertools</code> / <code>nltk</code> / <code>sklearn</code>;{' '}
        <code>*_r</code> shells out to <code>Rscript</code> inside the worker
        image.
      </>
    ),
    link: {to: '/docs/concepts/algorithm-families', label: 'Algorithm families →'},
  },
  {
    title: 'Docker-deployable cluster',
    description: (
      <>
        One published image (<code>albertogarob/whistlerlib</code>) for both
        scheduler and workers. Compose for dev, Swarm for prod.
      </>
    ),
    link: {to: '/docs/installation/docker', label: 'Docker install →'},
  },
];

function Feature({title, description, link}: FeatureItem) {
  return (
    <div className={clsx('col col--4', styles.feature)}>
      <div className="padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
        {link && (
          <Link to={link.to} className={styles.featureLink}>
            {link.label}
          </Link>
        )}
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
