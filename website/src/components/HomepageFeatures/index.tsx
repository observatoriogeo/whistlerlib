import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureIcon = {
  alt: string;
  className: string;
};

type FeatureItem = {
  title: string;
  description: ReactNode;
  link?: {to: string; label: string};
  icons?: FeatureIcon[];
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Distributed by default',
    description: (
      <>
        Built on <Link href="https://www.dask.org/">Dask</Link>. Hashtag,
        mention, and n-gram histograms fan out across your cluster and return
        as pandas DataFrames.
      </>
    ),
    link: {to: '/docs/concepts/architecture', label: 'Architecture →'},
    icons: [{alt: 'Dask', className: styles.iconDask}],
  },
  {
    title: 'Python or R, your choice',
    description: (
      <>
        Many analytics ship in two flavors. <code>*_alt_python</code> calls
        selected functions from{' '}
        <Link href="https://advertools.readthedocs.io/">
          <code>advertools</code>
        </Link>{' '}
        /{' '}
        <Link href="https://www.nltk.org/">
          <code>nltk</code>
        </Link>{' '}
        /{' '}
        <Link href="https://scikit-learn.org/">
          <code>sklearn</code>
        </Link>
        ; <code>*_r</code> shells out to <code>Rscript</code> with{' '}
        <Link href="https://cran.r-project.org/package=syuzhet">
          <code>syuzhet</code>
        </Link>{' '}
        inside the worker image.
      </>
    ),
    link: {to: '/docs/concepts/algorithm-families', label: 'Algorithm families →'},
    icons: [
      {alt: 'Python', className: styles.iconPython},
      {alt: 'R', className: styles.iconR},
    ],
  },
  {
    title: 'Docker-deployable cluster',
    description: (
      <>
        One published image (
        <Link href="https://hub.docker.com/r/albertogarob/whistlerlib">
          <code>albertogarob/whistlerlib</code>
        </Link>
        ) for both scheduler and workers. Compose for dev, Swarm for prod.
      </>
    ),
    link: {to: '/docs/installation/docker', label: 'Docker install →'},
    icons: [{alt: 'Docker', className: styles.iconDocker}],
  },
];

function Feature({title, description, link, icons}: FeatureItem) {
  return (
    <div className={clsx('col col--4', styles.feature)}>
      <div className="padding-horiz--md">
        {icons && icons.length > 0 && (
          <div className={styles.featureIcons}>
            {icons.map((icon) => (
              <span
                key={icon.alt}
                role="img"
                aria-label={icon.alt}
                title={icon.alt}
                className={clsx(styles.featureIcon, icon.className)}
              />
            ))}
          </div>
        )}
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
