import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';
import CodeBlock from '@theme/CodeBlock';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  const logoUrl = useBaseUrl('img/whistlerlib-logo-light.png');
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <img
          src={logoUrl}
          alt="Whistlerlib"
          className={styles.heroLogo}
        />
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.install}>
          <CodeBlock language="bash">pip install whistlerlib</CodeBlock>
        </div>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/installation/pip">
            Get started
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            to="/docs/tutorials/">
            Tutorials
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            href="https://github.com/observatoriogeo/whistlerlib">
            GitHub
          </Link>
        </div>
      </div>
    </header>
  );
}

type FeatureRowProps = {
  title: string;
  body: ReactNode;
  code: string;
  dark?: boolean;
  language?: string;
};

function FeatureRow({title, body, code, dark, language = 'python'}: FeatureRowProps) {
  return (
    <section className={clsx(styles.featureRow, dark && styles.featureRowDark)}>
      <div className={clsx('container', styles.featureRowInner)}>
        <div className={styles.featureRowText}>
          <Heading as="h2" className={styles.featureRowTitle}>
            {title}
          </Heading>
          <p>{body}</p>
        </div>
        <div className={styles.featureRowCode}>
          <CodeBlock language={language}>{code}</CodeBlock>
        </div>
      </div>
    </section>
  );
}

const HASHTAGS_CODE = `from whistlerlib import Context

ctx = Context('processes', '127.0.0.1', 8786)
ds = ctx.load_csv(
    filen='posts.csv',
    meta={
        'column_mapping': {'date_column': 'Date', 'text_column': 'text'},
        'file_encoding': 'utf-8',
    },
    num_partitions=8,
)

top5 = ds.hashtag_histogram_alt_python(k=5)
print(top5)`;

const DISPATCH_CODE = `# Pure Python (advertools-backed). No R install required on the worker.
ds.hashtag_histogram_alt_python(k=5)

# Same shape, different engine: R subprocess via the worker image.
# Wraps the 'tm' R package via Rscript per partition.
ds.hashtag_histogram_r(k=5)`;

const COONET_CODE = `# Returns (edges_df, igraph.Graph).
edges, g = ds.hashtag_weighted_coonet()

print(f"{g.vcount()} nodes, {g.ecount()} edges")
# Hand g to igraph for community detection, centrality, layouts:
communities = g.community_multilevel()`;

const SENTIMENT_CODE = `# Keep only rows whose Spanish sentiment score falls in [0.0, 0.5].
# Score is computed per-row via sentiment-analysis-spanish (TF/Keras),
# distributed across workers, then filtered with a boolean mask.
neutral_or_negative = ds.sentiment_range_spanish_alt_python(
    left_end=0.0,
    right_end=0.5,
)`;

const DOCKER_CODE = `# Bring up scheduler + 2 workers (Compose) on the local host.
docker compose -f docker/docker-compose.yml up -d

# Or pin to a published image tag:
WHISTLERLIB_TAG=0.2.0 docker compose -f docker/docker-compose.yml up -d

# Connect from your Python client:
#   from whistlerlib import Context
#   ctx = Context('processes', 'localhost', 8786)`;

const TIMEPROFILE_CODE = `# Every analytic accepts return_time_profile=True to get a per-stage
# timing breakdown alongside the result. Useful when tuning partition
# counts or comparing alt-python vs R implementations.
top5, profile = ds.hashtag_histogram_alt_python(
    k=5,
    return_time_profile=True,
)

print(profile)
# Stages are labelled <NN>_<name>_dist | _local so you can see which steps
# ran on the workers and which ran client-side.`;

function FeatureCallout() {
  return (
    <section className={styles.callout}>
      <div className="container">
        <Heading as="h2">Get started</Heading>
        <div className={styles.calloutInstall}>
          <CodeBlock language="bash">pip install whistlerlib</CodeBlock>
        </div>
        <div className={styles.buttons}>
          <Link className="button button--primary button--lg" to="/docs/quickstart">
            Quickstart
          </Link>
          <Link className="button button--primary button--lg" to="/docs/tutorials/">
            Tutorials
          </Link>
          <Link className="button button--primary button--lg" to="/docs/api/">
            API reference
          </Link>
          <Link
            className="button button--secondary button--lg"
            href="https://github.com/observatoriogeo/whistlerlib">
            GitHub
          </Link>
          <Link
            className="button button--secondary button--lg"
            href="https://pypi.org/project/whistlerlib/">
            PyPI
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <FeatureRow
          dark
          title="Hashtags, mentions, n-grams at scale"
          body={
            <>
              Wrap a CSV in a Dask DataFrame, then call a single method on the
              resulting <code>TweetDataset</code>. The top-k histogram fans out
              across the cluster as a <code>map_partitions</code> + distributed
              groupby, and lands back as a pandas DataFrame.
            </>
          }
          code={HASHTAGS_CODE}
        />
        <FeatureRow
          title="Two-layer dispatch: Python or R, same surface"
          body={
            <>
              Every analytic ships in matched <code>*_alt_python</code> /{' '}
              <code>*_r</code> pairs that compute the same shape with different
              per-partition extractors. The alt-Python layer covers most cases
              with zero R install; the R layer wraps <code>tm</code>,{' '}
              <code>syuzhet</code>, <code>RWeka</code>, and friends when you
              want their specific behavior.
            </>
          }
          code={DISPATCH_CODE}
        />
        <FeatureRow
          dark
          title="Co-occurrence networks as igraph.Graph"
          body={
            <>
              <code>hashtag_weighted_coonet</code> and{' '}
              <code>mention_weighted_coonet</code> return both an edge
              DataFrame and a ready-to-analyze <code>igraph.Graph</code>. Edges
              are sorted and deduplicated for deterministic output regardless
              of partition count.
            </>
          }
          code={COONET_CODE}
        />
        <FeatureRow
          title="Spanish sentiment ranges out of the box"
          body={
            <>
              <code>sentiment_range_spanish_alt_python</code> scores every row
              against the <code>sentiment-analysis-spanish</code> Keras model
              and returns only rows whose score lies in a chosen interval. The
              model is loaded per worker, the filter happens on the cluster.
            </>
          }
          code={SENTIMENT_CODE}
        />
        <FeatureRow
          dark
          title="R bridge inside a Docker worker"
          language="bash"
          body={
            <>
              The <code>albertogarob/whistlerlib</code> image bakes in R plus{' '}
              <code>tm</code>, <code>syuzhet</code>, <code>RWeka</code>,{' '}
              <code>radvertools</code>, and the system libraries they need.
              Both the scheduler and the workers use the same image; the
              scheduler just overrides the entrypoint to{' '}
              <code>dask-scheduler</code>. Your host never installs R.
            </>
          }
          code={DOCKER_CODE}
        />
        <FeatureRow
          title="Time profiling baked into every primitive"
          body={
            <>
              Pass <code>return_time_profile=True</code> to any analytic to get
              a <code>TimeProfile</code> alongside the result. Each stage is
              labeled with a <code>_dist</code> or <code>_local</code> suffix
              so you can see which steps ran on workers and which ran on the
              client.
            </>
          }
          code={TIMEPROFILE_CODE}
        />
        <FeatureCallout />
      </main>
    </Layout>
  );
}
